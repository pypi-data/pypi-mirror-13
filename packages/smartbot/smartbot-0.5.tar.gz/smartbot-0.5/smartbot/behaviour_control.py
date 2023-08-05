# coding: utf-8

class BehaviourControl(object):
    def __init__(self, bot):
        self.bot = bot
        self.behaviours = {}
        self.loadedBehaviours = {}

    def add(self, behaviourName, behaviour):
        behaviour = self.behaviours[behaviourName] = behaviour
        return behaviour

    def remove(self, behaviourName):
        return self.behaviours.pop(behaviourName)

    def hasBehaviour(self, behaviourName):
        return not not self.behaviours.get(behaviourName)

    def get(self, behaviourName):
        return self.behaviours.get(behaviourName)

    def getStatus(self, behaviourName):
        if not self.hasBehaviour(behaviourName):
            return 'unknown'
        elif behaviourName in self.loadedBehaviours:
            return 'loaded'
        else:
            return 'unloaded'

    def load(self, behaviourName):
        behaviour = self.behaviours[behaviourName]
        behaviour.load()
        self.loadedBehaviours[behaviourName] = behaviour
        return behaviour

    def unload(self, behaviourName):
        self.loadedBehaviours[behaviourName].unload()
        return self.loadedBehaviours.pop(behaviourName)

    def loadAll(self):
        [self.load(behaviourName) for behaviourName in self.behaviours if behaviourName not in self.loadedBehaviours]

    def unloadAll(self):
        loadedReversed = list(loadedBehaviours)
        loadedReversed.reverse()
        [self.unload(behaviourName) for behaviourName in (loadedReversed)]
