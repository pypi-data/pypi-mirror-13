# coding=utf-8
#
# This file is part of Hypothesis (https://github.com/DRMacIver/hypothesis)
#
# Most of this work is copyright (C) 2013-2015 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# https://github.com/DRMacIver/hypothesis/blob/master/CONTRIBUTING.rst for a
# full list of people who may hold copyright, and consult the git log if you
# need to determine who owns an individual contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
#
# END HEADER

"""This module provides the core primitives of Hypothesis, assume and given."""


from __future__ import division, print_function, absolute_import

import math
import time
import inspect
import binascii
import warnings
import functools
import traceback
from random import getstate as getglobalrandomstate
from random import Random
from itertools import islice
from collections import namedtuple

from hypothesis.errors import Flaky, Timeout, NoSuchExample, \
    Unsatisfiable, BadTemplateDraw, InvalidArgument, FailedHealthCheck, \
    UnsatisfiedAssumption, DefinitelyNoSuchExample, \
    HypothesisDeprecationWarning
from hypothesis.control import BuildContext
from hypothesis._settings import settings as Settings
from hypothesis._settings import Verbosity
from hypothesis.executors import executor, default_executor
from hypothesis.reporting import report, debug_report, verbose_report, \
    current_verbosity
from hypothesis.internal.compat import qualname, getargspec
from hypothesis.internal.tracker import Tracker
from hypothesis.internal.reflection import arg_string, impersonate, \
    copy_argspec, function_digest, fully_qualified_name, \
    convert_positional_arguments, get_pretty_function_description
from hypothesis.internal.examplesource import ParameterSource
from hypothesis.searchstrategy.strategies import SearchStrategy


def new_random():
    import random
    return random.Random(random.getrandbits(128))


def time_to_call_it_a_day(settings, start_time):
    """Have we exceeded our timeout?"""
    if settings.timeout <= 0:
        return False
    return time.time() >= start_time + settings.timeout


def find_satisfying_template(
    search_strategy, random, condition, tracker, settings, storage=None,
    max_parameter_tries=None,
):
    """Attempt to find a template for search_strategy such that condition is
    truthy.

    Exceptions other than UnsatisfiedAssumption will be immediately propagated.
    UnsatisfiedAssumption will indicate that similar examples should be avoided
    in future.

    Returns such a template as soon as it is found, otherwise stops after
    settings.max_examples examples have been considered or settings.timeout
    seconds have passed (if settings.timeout > 0).

    May raise a variety of exceptions depending on exact circumstances, but
    these will all subclass either Unsatisfiable (to indicate not enough
    examples were found which did not raise UnsatisfiedAssumption to consider
    this a valid test) or NoSuchExample (to indicate that this probably means
    that condition is true with very high probability).

    """
    satisfying_examples = 0
    examples_considered = 0
    timed_out = False
    max_iterations = max(settings.max_iterations, settings.max_examples)
    max_examples = min(max_iterations, settings.max_examples)
    min_satisfying_examples = min(
        settings.min_satisfying_examples,
        max_examples,
    )
    start_time = time.time()

    if storage:
        for example in storage.fetch(search_strategy):
            if examples_considered >= max_iterations:
                break
            examples_considered += 1
            if time_to_call_it_a_day(settings, start_time):
                break
            tracker.track(example)
            try:
                if condition(example):
                    return example
                satisfying_examples += 1
            except UnsatisfiedAssumption:
                pass
            if satisfying_examples >= max_examples:
                break

    parameter_source = ParameterSource(
        random=random, strategy=search_strategy,
        max_tries=max_parameter_tries,
    )

    assert search_strategy.template_upper_bound >= 0
    if isinstance(search_strategy.template_upper_bound, float):
        assert math.isinf(search_strategy.template_upper_bound)
    else:
        assert isinstance(search_strategy.template_upper_bound, int)

    for parameter in parameter_source:  # pragma: no branch
        if len(tracker) >= search_strategy.template_upper_bound:
            break
        if examples_considered >= max_iterations:
            break
        if satisfying_examples >= max_examples:
            break
        if time_to_call_it_a_day(settings, start_time):
            break
        examples_considered += 1

        try:
            example = search_strategy.draw_template(
                random, parameter
            )
        except BadTemplateDraw:
            debug_report('Failed attempt to draw a template')
            parameter_source.mark_bad()
            continue
        if tracker.track(example) > 1:
            debug_report('Skipping duplicate example')
            parameter_source.mark_bad()
            continue
        try:
            if condition(example):
                return example
        except UnsatisfiedAssumption:
            parameter_source.mark_bad()
            continue
        satisfying_examples += 1
    run_time = time.time() - start_time
    timed_out = settings.timeout >= 0 and run_time >= settings.timeout
    if (
        satisfying_examples and
        len(tracker) >= search_strategy.template_upper_bound
    ):
        raise DefinitelyNoSuchExample(
            get_pretty_function_description(condition),
            satisfying_examples,
        )
    elif satisfying_examples < min_satisfying_examples:
        if timed_out:
            raise Timeout((
                'Ran out of time before finding a satisfying example for '
                '%s. Only found %d examples (%d satisfying assumptions) in ' +
                '%.2fs.'
            ) % (
                get_pretty_function_description(condition),
                len(tracker), satisfying_examples, run_time
            ))
        else:
            raise Unsatisfiable((
                'Unable to satisfy assumptions of hypothesis %s. ' +
                'Only %d out of %d examples considered satisfied assumptions'
            ) % (
                get_pretty_function_description(condition),
                satisfying_examples, len(tracker)))
    else:
        raise NoSuchExample(get_pretty_function_description(condition))


def simplify_template_such_that(
    search_strategy, random, t, f, tracker, settings, start_time
):
    """Perform a greedy search to produce a "simplest" version of a template
    that satisfies some predicate.

    Care is taken to avoid cycles in simplify.

    f should produce the same result deterministically. This function may
    raise an error given f such that f(t) returns False sometimes and True
    some other times.

    If f throws UnsatisfiedAssumption this will be treated the same as if
    it returned False.

    """
    yield t

    try:
        if settings.max_shrinks <= 0 or not f(t):
            return
    except UnsatisfiedAssumption:
        return

    successful_shrinks = 0

    changed = True
    max_warmup = 5
    warmup = 0
    while (
        (changed or warmup < max_warmup) and
        successful_shrinks < settings.max_shrinks
    ):
        changed = False
        warmup += 1
        if warmup < max_warmup:
            debug_report('Running warmup simplification round %d' % (
                warmup
            ))
        elif warmup == max_warmup:
            debug_report('Warmup is done. Moving on to fully simplifying')

        any_simplifiers = False
        for simplify in search_strategy.simplifiers(random, t):
            debug_report('Applying simplification pass %s' % (
                simplify.__name__,
            ))
            any_simplifiers = True
            any_shrinks = False
            while successful_shrinks < settings.max_shrinks:
                simpler = simplify(random, t)
                if warmup < max_warmup:
                    simpler = islice(simpler, warmup)
                for s in simpler:
                    any_shrinks = True
                    if time_to_call_it_a_day(settings, start_time):
                        return
                    if tracker.track(s) > 1:
                        debug_report(
                            'Skipping simplifying to duplicate %s' % (
                                repr(s),
                            ))
                        continue
                    try:
                        if f(s):
                            successful_shrinks += 1
                            changed = True
                            yield s
                            t = s
                            break
                        else:
                            yield t
                    except UnsatisfiedAssumption:
                        pass
                else:
                    break
            if not any_shrinks:
                debug_report('No shrinks possible')
        if not any_simplifiers:
            debug_report('No simplifiers for template %s' % (
                repr(t),
            ))
            break


def best_satisfying_template(
    search_strategy, random, condition, settings, storage, tracker=None,
    max_parameter_tries=None, start_time=None,
):
    """Find and then minimize a satisfying template.

    First look in storage if it is not None, then attempt to generate
    one. May throw all the exceptions of find_satisfying_template. Once
    an example has been found it will be further minimized.

    """
    if tracker is None:
        tracker = Tracker()
    if start_time is None:
        start_time = time.time()

    successful_shrinks = -1
    with settings:
        satisfying_example = find_satisfying_template(
            search_strategy, random, condition, tracker, settings, storage,
            max_parameter_tries=max_parameter_tries,
        )
        for simpler in simplify_template_such_that(
            search_strategy, random, satisfying_example, condition, tracker,
            settings, start_time,
        ):
            successful_shrinks += 1
            satisfying_example = simpler
        if storage is not None:
            storage.save(satisfying_example, search_strategy)
        if not successful_shrinks:
            verbose_report('Could not shrink example')
        elif successful_shrinks == 1:
            verbose_report('Successfully shrunk example once')
        else:
            verbose_report(
                'Successfully shrunk example %d times' % (
                    successful_shrinks,))
        return satisfying_example


def test_is_flaky(test, expected_repr):
    @functools.wraps(test)
    def test_or_flaky(*args, **kwargs):
        text_repr = arg_string(test, args, kwargs)
        if text_repr == expected_repr:
            raise Flaky(
                (
                    'Hypothesis %s(%s) produces unreliable results: Falsified'
                    ' on the first call but did not on a subsequent one'
                ) % (test.__name__, text_repr,))
        else:
            raise Flaky(
                (
                    'Hypothesis %s produces unreliable results: Falsified'
                    ' on the first call but did not on a subsequent one.'
                    ' This is possibly due to unreliable values, which may '
                    'be a bug in the strategy.\nCall 1: %s\nCall 2: %s\n'
                ) % (test.__name__, expected_repr, text_repr,))
    return test_or_flaky


Example = namedtuple('Example', ('args', 'kwargs'))


def example(*args, **kwargs):
    """Add an explicit example called with these args and kwargs to the
    test."""
    if args and kwargs:
        raise InvalidArgument(
            'Cannot mix positional and keyword arguments for examples'
        )
    if not (args or kwargs):
        raise InvalidArgument(
            'An example must provide at least one argument'
        )

    def accept(test):
        if not hasattr(test, 'hypothesis_explicit_examples'):
            test.hypothesis_explicit_examples = []
        test.hypothesis_explicit_examples.append(Example(tuple(args), kwargs))
        return test
    return accept


def reify_and_execute(
    search_strategy, template, test,
    print_example=False, record_repr=None,
    is_final=False,
):
    def run():
        with BuildContext(is_final=is_final):
            args, kwargs = search_strategy.reify(template)
            text_version = arg_string(test, args, kwargs)
            if print_example:
                report(
                    lambda: 'Falsifying example: %s(%s)' % (
                        test.__name__, text_version,))
            elif current_verbosity() >= Verbosity.verbose:
                report(
                    lambda: 'Trying example: %s(%s)' % (
                        test.__name__, text_version))
            if record_repr is not None:
                record_repr[0] = text_version
            return test(*args, **kwargs)
    return run


def seed(seed):
    """
    seed: Start the test execution from a specific seed. May be any hashable
          object. No exact meaning for seed is provided other than that
          for a fixed seed value Hypothesis will try the same actions (insofar
          as it can given external sources of non-determinism. e.g. timing and
          hash randomization).
          Overrides the derandomize setting if it is present.
    """

    def accept(test):
        test._hypothesis_internal_use_seed = seed
        return test
    return accept


def given(*generator_arguments, **generator_kwargs):
    """A decorator for turning a test function that accepts arguments into a
    randomized test.

    This is the main entry point to Hypothesis. See the full tutorial
    for details of its behaviour.

    """
    def run_test_with_generator(test):
        original_argspec = getargspec(test)

        def invalid(message):
            def wrapped_test(*arguments, **kwargs):
                raise InvalidArgument(message)
            return wrapped_test

        if not (generator_arguments or generator_kwargs):
            return invalid(
                'given must be called with at least one argument')

        if (
            generator_arguments and (
                original_argspec.varargs or original_argspec.keywords)
        ):
            return invalid(
                'varargs or keywords are not supported with positional '
                'arguments to @given'
            )

        if (
            len(generator_arguments) > len(original_argspec.args)
        ):
            return invalid((
                'Too many positional arguments for %s() (got %d but'
                ' expected at most %d') % (
                    test.__name__, len(generator_arguments),
                    len(original_argspec.args)))

        if generator_arguments and generator_kwargs:
            return invalid(
                'cannot mix positional and keyword arguments to @given'
            )
        extra_kwargs = [
            k for k in generator_kwargs if k not in original_argspec.args]
        if extra_kwargs and not original_argspec.keywords:
            return invalid(
                '%s() got an unexpected keyword argument %r' % (
                    test.__name__,
                    extra_kwargs[0]
                ))
        arguments = original_argspec.args
        for a in arguments:
            if isinstance(a, list):  # pragma: no cover
                return invalid((
                    'Cannot decorate function %s() because it has '
                    'destructuring arguments') % (
                        test.__name__,
                ))
        if original_argspec.defaults:
            return invalid(
                'Cannot apply @given to a function with defaults.'
            )
        for name, strategy in zip(
            arguments[-len(generator_arguments):], generator_arguments
        ):
            generator_kwargs[name] = strategy

        argspec = inspect.ArgSpec(
            args=[a for a in arguments if a not in generator_kwargs],
            keywords=original_argspec.keywords,
            varargs=original_argspec.varargs,
            defaults=None
        )

        @impersonate(test)
        @copy_argspec(
            test.__name__, argspec
        )
        def wrapped_test(*arguments, **kwargs):
            settings = wrapped_test._hypothesis_internal_use_settings
            if wrapped_test._hypothesis_internal_use_seed is not None:
                random = Random(
                    wrapped_test._hypothesis_internal_use_seed)
            elif settings.derandomize:
                random = Random(function_digest(test))
            else:
                random = new_random()

            import hypothesis.strategies as sd

            selfy = None
            arguments, kwargs = convert_positional_arguments(
                wrapped_test, arguments, kwargs)

            # If the test function is a method of some kind, the bound object
            # will be the first named argument if there are any, otherwise the
            # first vararg (if any).
            if argspec.args:
                selfy = kwargs.get(argspec.args[0])
            elif arguments:
                selfy = arguments[0]
            test_runner = executor(selfy)

            for example in reversed(getattr(
                wrapped_test, 'hypothesis_explicit_examples', ()
            )):
                if example.args:
                    example_kwargs = dict(zip(
                        original_argspec.args[-len(example.args):],
                        example.args
                    ))
                else:
                    example_kwargs = example.kwargs
                example_kwargs.update(kwargs)
                # Note: Test may mutate arguments and we can't rerun explicit
                # examples, so we have to calculate the failure message at this
                # point rather than than later.
                message_on_failure = 'Falsifying example: %s(%s)' % (
                    test.__name__, arg_string(test, arguments, example_kwargs)
                )
                try:
                    with BuildContext() as b:
                        test_runner(
                            lambda: test(*arguments, **example_kwargs)
                        )
                except BaseException:
                    report(message_on_failure)
                    for n in b.notes:
                        report(n)
                    raise

            arguments = tuple(arguments)

            given_specifier = sd.tuples(
                sd.just(arguments),
                sd.fixed_dictionaries(generator_kwargs).map(
                    lambda args: dict(args, **kwargs)
                )
            )

            def fail_health_check(message):
                message += (
                    '\nSee http://hypothesis.readthedocs.org/en/latest/health'
                    'checks.html for more information about this.'
                )
                if settings.strict:
                    raise FailedHealthCheck(message)
                else:
                    warnings.warn(FailedHealthCheck(message))

            search_strategy = given_specifier
            search_strategy.validate()

            if settings.database:
                storage = settings.database.storage(
                    fully_qualified_name(test))
            else:
                storage = None

            start = time.time()
            warned_random = [False]
            perform_health_check = settings.perform_health_check
            if Settings.default is not None:
                perform_health_check &= Settings.default.perform_health_check

            if perform_health_check:
                initial_state = getglobalrandomstate()
                health_check_random = Random(random.getrandbits(128))
                count = 0
                bad_draws = 0
                filtered_draws = 0
                errors = 0
                while (
                    count < 10 and time.time() < start + 1 and
                    filtered_draws < 50 and bad_draws < 50
                ):
                    try:
                        with Settings(settings, verbosity=Verbosity.quiet):
                            test_runner(reify_and_execute(
                                search_strategy,
                                search_strategy.draw_template(
                                    health_check_random,
                                    search_strategy.draw_parameter(
                                        health_check_random,
                                    )),
                                lambda *args, **kwargs: None,
                            ))
                        count += 1
                    except BadTemplateDraw:
                        bad_draws += 1
                    except UnsatisfiedAssumption:
                        filtered_draws += 1
                    except Exception:
                        if errors == 0:
                            report(traceback.format_exc())
                        errors += 1
                        if test_runner is default_executor:
                            fail_health_check(
                                'An exception occurred during data '
                                'generation in initial health check. '
                                'This indicates a bug in the strategy. '
                                'This could either be a Hypothesis bug or '
                                "an error in a function yo've passed to "
                                'it to construct your data.'
                            )
                        else:
                            fail_health_check(
                                'An exception occurred during data '
                                'generation in initial health check. '
                                'This indicates a bug in the strategy. '
                                'This could either be a Hypothesis bug or '
                                'an error in a function you\'ve passed to '
                                'it to construct your data. Additionally, '
                                'you have a custom executor, which means '
                                'that this could be your executor failing '
                                'to handle a function which returns None. '
                            )
                if filtered_draws >= 50:
                    fail_health_check((
                        'It looks like your strategy is filtering out a lot '
                        'of data. Health check found %d filtered examples but '
                        'only %d good ones. This will make your tests much '
                        'slower, and also will probably distort the data '
                        'generation quite a lot. You should adapt your '
                        'strategy to filter less.') % (
                        filtered_draws, count
                    ))
                if bad_draws >= 50:
                    fail_health_check(
                        'Hypothesis is struggling to generate examples. '
                        'This is often a sign of a recursive strategy which '
                        'fans out too broadly. If you\'re using recursive, '
                        'try to reduce the size of the recursive step or '
                        'increase the maximum permitted number of leaves.'
                    )
                runtime = time.time() - start
                if runtime > 1.0 or count < 10:
                    fail_health_check((
                        'Data generation is extremely slow: Only produced '
                        '%d valid examples in %.2f seconds. Try decreasing '
                        "size of the data yo're generating (with e.g."
                        'average_size or max_leaves parameters).'
                    ) % (count, runtime))
                if getglobalrandomstate() != initial_state:
                    warned_random[0] = True
                    fail_health_check(
                        'Data generation depends on global random module. '
                        'This makes results impossible to replay, which '
                        'prevents Hypothesis from working correctly. '
                        'If you want to use methods from random, use '
                        'randoms() from hypothesis.strategies to get an '
                        'instance of Random you can use. Alternatively, you '
                        'can use the random_module() strategy to explicitly '
                        'seed the random module.'
                    )

            last_exception = [None]
            repr_for_last_exception = [None]

            def is_template_example(xs):
                if perform_health_check and not warned_random[0]:
                    initial_state = getglobalrandomstate()
                record_repr = [None]
                try:
                    result = test_runner(reify_and_execute(
                        search_strategy, xs, test,
                        record_repr=record_repr,
                    ))
                    if result is not None and settings.perform_health_check:
                        raise FailedHealthCheck((
                            'Tests run under @given should return None, but '
                            '%s returned %r instead.'
                        ) % (test.__name__, result), settings)
                    return False
                except (
                    HypothesisDeprecationWarning, FailedHealthCheck,
                    UnsatisfiedAssumption
                ):
                    raise
                except Exception:
                    last_exception[0] = traceback.format_exc()
                    repr_for_last_exception[0] = record_repr[0]
                    verbose_report(last_exception[0])
                    return True
                finally:
                    if (
                        not warned_random[0] and
                        perform_health_check and
                        getglobalrandomstate() != initial_state
                    ):
                        warned_random[0] = True
                        fail_health_check(
                            'Your test used the global random module. '
                            'This is unlikely to work correctly. You should '
                            'consider using the randoms() strategy from '
                            'hypothesis.strategies instead. Alternatively, '
                            'you can use the random_module() strategy to '
                            'explicitly seed the random module.'
                        )
            is_template_example.__name__ = test.__name__
            is_template_example.__qualname__ = qualname(test)

            with settings:
                falsifying_template = None
                try:
                    falsifying_template = best_satisfying_template(
                        search_strategy, random, is_template_example,
                        settings, storage, start_time=start,
                    )
                except NoSuchExample:
                    return

                assert last_exception[0] is not None

                try:
                    test_runner(reify_and_execute(
                        search_strategy, falsifying_template, test,
                        print_example=True, is_final=True
                    ))
                except UnsatisfiedAssumption:
                    report(traceback.format_exc())
                    raise Flaky(
                        'Unreliable assumption: An example which satisfied '
                        'assumptions on the first run now fails it.'
                    )

                report(
                    'Failed to reproduce exception. Expected: \n' +
                    last_exception[0],
                )

                try:
                    test_runner(reify_and_execute(
                        search_strategy, falsifying_template,
                        test_is_flaky(test, repr_for_last_exception[0]),
                        print_example=True, is_final=True
                    ))
                except UnsatisfiedAssumption:
                    raise Flaky(
                        'Unreliable test data: Failed to reproduce a failure '
                        'and then when it came to recreating the example in '
                        'order to print the test data with a flaky result '
                        'the example was filtered out (by e.g. a '
                        'call to filter in your strategy) when we didn\'t '
                        'expect it to be.'
                    )
        for attr in dir(test):
            if attr[0] != '_' and not hasattr(wrapped_test, attr):
                setattr(wrapped_test, attr, getattr(test, attr))
        wrapped_test.is_hypothesis_test = True
        wrapped_test._hypothesis_internal_use_seed = getattr(
            test, '_hypothesis_internal_use_seed', None
        )
        wrapped_test._hypothesis_internal_use_settings = getattr(
            test, '_hypothesis_internal_use_settings', None
        ) or Settings.default
        return wrapped_test
    return run_test_with_generator


def find(specifier, condition, settings=None, random=None, storage=None):
    settings = settings or Settings(
        max_examples=2000,
        min_satisfying_examples=0,
        max_shrinks=2000,
    )

    if not isinstance(specifier, SearchStrategy):
        raise InvalidArgument(
            'Expected SearchStrategy but got %r of type %s' % (
                specifier, type(specifier).__name__
            ))

    search = specifier

    if storage is None and settings.database is not None:
        storage = settings.database.storage(
            'find(%s)' % (
                binascii.hexlify(function_digest(condition)).decode('ascii'),
            )
        )

    random = random or new_random()
    successful_examples = [0]

    def template_condition(template):
        with BuildContext():
            result = search.reify(template)
            success = condition(result)

        if success:
            successful_examples[0] += 1

        if not successful_examples[0]:
            verbose_report(lambda: 'Trying example %s' % (
                repr(result),
            ))
        elif success:
            if successful_examples[0] == 1:
                verbose_report(lambda: 'Found satisfying example %s' % (
                    repr(result),
                ))
            else:
                verbose_report(lambda: 'Shrunk example to %s' % (
                    repr(result),
                ))
        return success

    template_condition.__name__ = condition.__name__
    tracker = Tracker()

    try:
        template = best_satisfying_template(
            search, random, template_condition, settings,
            tracker=tracker, max_parameter_tries=2,
            storage=storage,
        )
        with BuildContext(is_final=True, close_on_capture=False):
            return search.reify(template)
    except Timeout:
        raise
    except NoSuchExample:
        if search.template_upper_bound <= len(tracker):
            raise DefinitelyNoSuchExample(
                get_pretty_function_description(condition),
                search.template_upper_bound,
            )
        raise NoSuchExample(get_pretty_function_description(condition))
