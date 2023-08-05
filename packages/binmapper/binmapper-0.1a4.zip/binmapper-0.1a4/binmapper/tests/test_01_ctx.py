import unittest
import binmapper
import textwrap
from binmapper.parser.template_context import TemplateContext


class testCtx(unittest.TestCase):

    def setUp(self):
        pass

    def test_01_set(self):
        ctx = TemplateContext()
        ctx.set(a = 1)
        self.assertEqual(ctx.raw()['a'], 1)

    def test_02_get(self):
        ctx = TemplateContext()
        ctx.set(a = 1)
        a = ctx.get('a')
        self.assertEqual(a, 1)

    def test_03_append(self):
        ctx = TemplateContext()
        ctx.append(a = 1)
        ctx.append(a = 2)
        a = ctx.get('a')
        self.assertEqual(a, [1, 2])

    def test_04_capture(self):
        ctx = TemplateContext()
        ctx.start_capture("c")
        ctx.end_capture()
        self.assertEqual(ctx.raw()['c'], [])

    def test_04_capture_set(self):
        ctx = TemplateContext()
        ctx.start_capture("c")
        ctx.set(a = 1)
        ctx.next_capture()
        ctx.end_capture()
        self.assertEqual(ctx.raw()['c'][0]['a'], 1)

    def test_05_capture_get(self):
        ctx = TemplateContext()
        ctx.start_capture("c")
        ctx.set(a = 1)
        a = ctx.get('a')
        ctx.next_capture()
        ctx.end_capture()
        self.assertEqual(a, 1)

    def test_06_capture_append(self):
        ctx = TemplateContext()
        ctx.start_capture("c")
        ctx.append(a = 1)
        ctx.append(a = 2)
        ctx.next_capture()
        ctx.end_capture()
        self.assertEqual(ctx.raw()['c'][0]['a'], [1, 2])

    def test_07_capture_append_list(self):
        ctx = TemplateContext()
        ctx.start_capture("c")
        ctx.append(a = [1])
        ctx.append(a = [2])
        ctx.append(a = 3)
        ctx.append(b = {"x": 1})
        ctx.append(b = {"y": 2})
        ctx.next_capture()
        ctx.end_capture()
        self.assertEqual(ctx.raw()['c'][0]['a'], [1, 2, 3])
        self.assertEqual(ctx.raw()['c'][0]['b'], {"x": 1, "y": 2})

    def test_08_capture_set_stage(self):
        ctx = TemplateContext()
        ctx.start_capture("c")
        ctx.set(a = 1)
        ctx.next_capture()
        ctx.set(a = 2)
        ctx.next_capture()
        ctx.end_capture()
        self.assertEqual(ctx.raw()['c'][0]['a'], 1)
        self.assertEqual(ctx.raw()['c'][1]['a'], 2)

    def test_09_capture_stack(self):
        ctx = TemplateContext()
        ctx.start_capture("c")

        ctx.start_capture("e")
        ctx.set(a = 1)
        ctx.next_capture()
        ctx.set(a = 2)
        ctx.next_capture()
        ctx.end_capture()

        ctx.next_capture()

        ctx.start_capture("e")
        ctx.set(a = 3)
        ctx.next_capture()
        ctx.set(a = 4)
        ctx.next_capture()
        ctx.end_capture()

        ctx.end_capture()
        # print ctx.raw()['c']
        self.assertEqual(ctx.raw()['c'][0]['e'][0]['a'], 1)
        self.assertEqual(ctx.raw()['c'][0]['e'][1]['a'], 2)
        self.assertEqual(ctx.raw()['c'][1]['e'][0]['a'], 3)
        self.assertEqual(ctx.raw()['c'][1]['e'][1]['a'], 4)


if __name__ == '__main__':
    unittest.main()
