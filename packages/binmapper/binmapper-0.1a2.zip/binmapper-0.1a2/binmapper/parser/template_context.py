# Copyright 2015 RedSkotina
# Licensed under the Apache License, Version 2.0

""" Extended context for jinja2.

"""

class Stage(object):

    def __init__(self, root, idx):
        self.root = root
        self.idx = idx


class TemplateContext(object):

    def __init__(self):
        root = []
        idx = 0
        stage = Stage(root, idx)
        self.stage_stack = [stage]

    def get(self, key):
        stage = self.stage_stack[-1]
        z = stage.root[stage.idx]
        return z[key]

    def set(self, **kwargs):
        stage = self.stage_stack[-1]
        if len(stage.root) <= stage.idx:
            stage.root.append({})
        z = stage.root[stage.idx]
        z.update(kwargs)
        stage.root[stage.idx] = z

    def raw(self):
        return self.stage_stack[0].root[0]

    def append(self, **kwargs):
        stage = self.stage_stack[-1]
        if len(stage.root) <= stage.idx:
            stage.root.append({})

        z = stage.root[stage.idx].copy()
        for key in kwargs:
            if key in z:
                if isinstance(z[key], list):
                    if isinstance(kwargs[key], list):
                        z[key].extend(kwargs[key])
                    else:
                        z[key].append(kwargs[key])
                elif isinstance(z[key], dict):
                    z[key].update(kwargs[key])
                else:
                    z[key] = [z[key], kwargs[key]]
            else:
                z[key] = kwargs[key]

        stage.root[stage.idx] = z

    def start_capture(self, key):

        last_stage = self.stage_stack[-1]
        if len(last_stage.root) <= last_stage.idx:
            last_stage.root.append({})
        last_stage.root[last_stage.idx][key] = []
        stage = Stage(last_stage.root[last_stage.idx][key], 0)
        self.stage_stack.append(stage)

    def next_capture(self):
        stage = self.stage_stack[-1]
        stage.idx += 1

    def end_capture(self):
        self.stage_stack.pop()
