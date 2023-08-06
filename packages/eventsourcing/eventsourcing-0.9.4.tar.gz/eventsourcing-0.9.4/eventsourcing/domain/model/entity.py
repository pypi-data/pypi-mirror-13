from abc import ABCMeta, abstractmethod
from inspect import isfunction
from six import with_metaclass
from eventsourcing.domain.model.events import DomainEvent, publish, QualnameABCMeta


class EventSourcedEntity(with_metaclass(QualnameABCMeta)):

    class Created(DomainEvent):
        def __init__(self, entity_version=0, **kwargs):
            super(EventSourcedEntity.Created, self).__init__(entity_version=entity_version, **kwargs)

    class AttributeChanged(DomainEvent):
        pass

    class Discarded(DomainEvent):
        pass

    def __init__(self, entity_id, entity_version, timestamp):
        self._id = entity_id
        self._version = entity_version
        self._is_discarded = False
        self._created_on = timestamp

    def _increment_version(self):
        self._version += 1

    def _assert_not_discarded(self):
        assert not self._is_discarded

    @property
    def id(self):
        return self._id

    def _validate_originator(self, event):
        assert self.id == event.entity_id, (self.id, event.entity_id)
        assert self._version == event.entity_version, "{} != {}".format(self._version, event.entity_version)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def _change_attribute_value(self, name, value):
        self._assert_not_discarded()
        event = self.AttributeChanged(name=name, value=value, entity_id=self._id, entity_version=self._version)
        self._apply(event)
        publish(event)

    def discard(self):
        self._assert_not_discarded()
        event = self.Discarded(entity_id=self._id, entity_version=self._version)
        self._apply(event)
        publish(event)

    def _apply(self, event):
        self.mutator(self, event)

    @classmethod
    def mutator(cls, entity=None, event=None):
        # assert isinstance(event, DomainEvent), "Not a domain event: {}".format(event)
        event_class = type(event)
        if event_class == cls.Created:
            # assert isinstance(entity, type), entity
            assert entity is None, "Are there multiple Created events for the same ID? %s, %s" % (entity, event)
            entity_class = cls
            entity = entity_class(**event.__dict__)
            # assert isinstance(entity, EventSourcedEntity), entity
            entity._increment_version()
            return entity

        elif event_class == cls.AttributeChanged:
            # assert isinstance(entity, EventSourcedEntity), entity
            entity._validate_originator(event)
            setattr(entity, event.name, event.value)
            entity._increment_version()
            return entity

        elif event_class == cls.Discarded:
            # assert isinstance(entity, EventSourcedEntity), entity
            entity._validate_originator(event)
            entity._is_discarded = True
            entity._increment_version()
            return None
        else:
            raise NotImplementedError(repr(event_class))


def eventsourcedproperty(*args, **kwargs):
    if len(args) == 1 and len(kwargs) == 0 and isfunction(args[0]):
        getter = args[0]

        def setter(self, value):
            assert isinstance(self, EventSourcedEntity), self
            self._change_attribute_value(name='_' + getter.__name__, value=value)

        return property(fget=getter, fset=setter)
    else:
        # Decorator has arguments...
        return eventsourcedproperty


class EntityRepository(with_metaclass(ABCMeta)):

    @abstractmethod
    def __getitem__(self, entity_id):
        """Returns entity for given ID.
        """

    @abstractmethod
    def __contains__(self, entity_id):
        """Returns True or False, according to whether or not entity exists.
        """
