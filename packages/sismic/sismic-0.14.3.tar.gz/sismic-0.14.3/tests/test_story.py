import unittest
from sismic import io
from sismic.interpreter import Interpreter
from sismic.model import MacroStep, MicroStep
from sismic.stories import *


class StoryTests(unittest.TestCase):
    def test_storycreation(self):
        story = Story()
        story.append(Event('a'))
        story.append(Event('b'))
        story.append(Pause(10))
        story.append(Event('c'))

        self.assertEqual(len(story), 4)

    def test_tell(self):
        story = Story([Event('goto s2'), Pause(5), Event('goto final')])
        sc = io.import_from_yaml(open('tests/yaml/simple.yaml'))
        interpreter = Interpreter(sc)
        story.tell(interpreter)

        self.assertTrue(interpreter.final)
        self.assertEqual(interpreter.time, 5)
        self.assertEqual(len(interpreter.trace), 4)


class RandomStoryTests(unittest.TestCase):
    def setUp(self):
        self.story = Story([Event('a'), Event('b'), Event('c'), Pause(1), Pause(2)])

    def test_length(self):
        self.assertEqual(len(next(random_stories_generator(self.story))), 5)
        self.assertEqual(len(next(random_stories_generator(self.story, length=3))), 3)
        self.assertEqual(len(next(random_stories_generator(self.story, length=6))), 6)
        self.assertEqual(len(next(random_stories_generator([]))), 0)

    def test_number(self):
        self.assertEqual(len(list(random_stories_generator(self.story, number=10))), 10)


class StoryFromTraceTests(unittest.TestCase):
    def test_empty_trace(self):
        trace = []
        self.assertListEqual(story_from_trace(trace), [])

    def test_events(self):
        trace = [
            MacroStep(0, [MicroStep(Event('a'))]),
            MacroStep(0, [MicroStep(Event('b'))]),
            MacroStep(0, [MicroStep(Event('c'))]),
            MacroStep(0, [MicroStep(Event('d'))]),
        ]
        self.assertListEqual(story_from_trace(trace), [
            Event('a'), Event('b'), Event('c'), Event('d')
        ])

    def test_pauses(self):
        trace = [
            MacroStep(0, []),
            MacroStep(10, []),
            MacroStep(10, []),
            MacroStep(15, []),
        ]
        self.assertListEqual(story_from_trace(trace), [
            Pause(10), Pause(5)
        ])

    def test_initial_pause(self):
        trace = [MacroStep(10, [])]
        self.assertListEqual(story_from_trace(trace), [Pause(10)])

    def test_events_and_pauses(self):
        trace = [
            MacroStep(2, [MicroStep(Event('a'))]),
            MacroStep(5, [MicroStep(Event('b'))]),
            MacroStep(9, [MicroStep(Event('c'))]),
            MacroStep(14, [MicroStep(Event('d'))]),
        ]
        self.assertListEqual(story_from_trace(trace), [
            Pause(2), Event('a'), Pause(3), Event('b'), Pause(4), Event('c'), Pause(5), Event('d')
        ])
