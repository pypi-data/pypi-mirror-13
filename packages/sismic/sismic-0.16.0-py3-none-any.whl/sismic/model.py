from functools import lru_cache


class Event:
    """
    Simple event with a name and (optionally) some data.
    Unless the attribute already exists, each key from ``data`` is exposed as an attribute
    of this class.

    :param name: Name of the event
    :param data: additional data (mapping, dict-like)
    """

    def __init__(self, name: str, **additional_parameters):
        self.name = name
        self.data = additional_parameters

    def __eq__(self, other):
        return isinstance(other, Event) and self.name == other.name

    def __getattr__(self, attr):
        return self.data[attr]

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        if self.data:
            return '{}({}, {})'.format(self.__class__.__name__, self.name, ', '.join('{}={}'.format(k, v) for k,v in self.data.items()))
        else:
            return '{}({})'.format(self.__class__.__name__, self.name)


class InternalEvent(Event):
    """
    Subclass of Event that represents an internal event.
    """
    pass


class ContractMixin:
    """
    Mixin with a contract: preconditions, postconditions and invariants.
    """

    def __init__(self):
        self._preconditions = []
        self._postconditions = []
        self._invariants = []

    @property
    def preconditions(self):
        """
        A list of preconditions (str).
        """
        return self._preconditions

    @property
    def postconditions(self):
        """
        A list of postconditions (str).
        """
        return self._postconditions

    @property
    def invariants(self):
        """
        A list of invariants (str).
        """
        return self._invariants


class StateMixin:
    """
    State element with a name.

    :param name: name of the state
    """

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.name)

    def __eq__(self, other):
        return isinstance(other, StateMixin) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class ActionStateMixin:
    """
    State that can define actions on entry and on exit.

    :param on_entry: code to execute when state is entered
    :param on_exit: code to execute when state is exited
    """

    def __init__(self, on_entry: str = None, on_exit: str = None):
        self._on_entry = on_entry
        self._on_exit = on_exit

    @property
    def on_entry(self):
        return self._on_entry

    @property
    def on_exit(self):
        return self._on_exit


class TransitionStateMixin:
    """
    A simple state can host transitions
    """

    def __init__(self):
        self._transitions = []

    @property
    def transitions(self):
        return self._transitions


class CompositeStateMixin:
    """
    Composite state can have children states.
    """

    def __init__(self):
        self._children = []

    @property
    def children(self):
        return self._children


class BasicState(ContractMixin, StateMixin, TransitionStateMixin, ActionStateMixin):
    """
    A basic state, with a name, transitions, actions, etc. but no child state.

    :param name: name of this state
    :param on_entry: code to execute when state is entered
    :param on_exit: code to execute when state is exited
    """

    def __init__(self, name: str, on_entry: str = None, on_exit: str = None):
        ContractMixin.__init__(self)
        StateMixin.__init__(self, name)
        TransitionStateMixin.__init__(self)
        ActionStateMixin.__init__(self, on_entry, on_exit)


class CompoundState(ContractMixin, StateMixin, TransitionStateMixin, ActionStateMixin, CompositeStateMixin):
    """
    Compound states must have children states.

    :param name: name of this state
    :param initial: name of the initial state
    :param on_entry: code to execute when state is entered
    :param on_exit: code to execute when state is exited
    """

    def __init__(self, name: str, initial: str = None, on_entry: str = None, on_exit: str = None):
        ContractMixin.__init__(self)
        StateMixin.__init__(self, name)
        TransitionStateMixin.__init__(self)
        ActionStateMixin.__init__(self, on_entry, on_exit)
        CompositeStateMixin.__init__(self)
        self.initial = initial


class OrthogonalState(ContractMixin, StateMixin, TransitionStateMixin, ActionStateMixin, CompositeStateMixin):
    """
    Orthogonal states run their children simultaneously.

    :param name: name of this state
    :param on_entry: code to execute when state is entered
    :param on_exit: code to execute when state is exited
    """

    def __init__(self, name: str, on_entry: str = None, on_exit: str = None):
        ContractMixin.__init__(self)
        StateMixin.__init__(self, name)
        TransitionStateMixin.__init__(self)
        ActionStateMixin.__init__(self, on_entry, on_exit)
        CompositeStateMixin.__init__(self)


class HistoryState(ContractMixin, StateMixin):
    """
    History state can be either 'shallow' (default) or 'deep'.
    A shallow history state resumes the execution of its parent.
    A deep history state resumes the execution of its parent, and of every nested
    active states in its parent.

    :param name: name of this state
    :param initial: name of the initial state
    :param deep: Boolean indicating whether a deep semantic (True) or a shallow semantic (False) should be used
    """

    def __init__(self, name: str, initial: str = None, deep: bool = False):
        ContractMixin.__init__(self)
        StateMixin.__init__(self, name)
        self.name = name
        self.initial = initial
        self.deep = deep


class FinalState(ContractMixin, StateMixin, ActionStateMixin):
    """
    Final state has NO transition and is used to detect state machine termination.

    :param name: name of this state
    :param on_entry: code to execute when state is entered
    :param on_exit: code to execute when state is exited
    """

    def __init__(self, name: str, on_entry: str = None, on_exit: str = None):
        ContractMixin.__init__(self)
        StateMixin.__init__(self, name)
        ActionStateMixin.__init__(self, on_entry, on_exit)


class Transition(ContractMixin):
    """
    A Transition between two states.
    Transition can be eventless or internal (but not both at once).
    A condition (code as string) can be specified as a guard.

    :param from_state: name of the source state
    :param to_state: name of the target state (if transition is not internal)
    :param event: event (if any)
    :param guard: condition as code (if any)
    :param action: action as code (if any)
    """

    def __init__(self, from_state: str, to_state: str = None, event: Event = None, guard: str = None,
                 action: str = None):
        ContractMixin.__init__(self)
        self.from_state = from_state
        self.to_state = to_state
        self.event = event
        self.guard = guard
        self.action = action

    @property
    def internal(self):
        """
        Boolean indicating whether this transition is an internal transition.
        """
        return self.to_state is None

    @property
    def eventless(self):
        """
        Boolean indicating whether this transition is an eventless transition.
        """
        return self.event is None

    def __eq__(self, other):
        return (isinstance(other, Transition) and
                self.from_state == other.from_state and
                self.to_state == other.to_state and
                self.event == other.event)

    def __repr__(self):
        return 'Transition({0}, {1}, {2})'.format(self.from_state, self.to_state, self.event)

    def __str__(self):
        to_state = self.to_state if self.to_state else '[' + self.from_state + ']'
        event = '+' + self.event.name if self.event else ''
        return self.from_state + event + ' -> ' + to_state

    def __hash__(self):
        return hash(self.from_state)


class StateChart(ContractMixin, StateMixin, ActionStateMixin, CompositeStateMixin):
    """
    Python structure for a statechart

    :param name: Name of this statechart
    :param initial: Initial state
    :param on_entry: Code to execute when this statechart is initialized for execution
    """

    def __init__(self, name: str, initial: str, on_entry: str = None):
        ContractMixin.__init__(self)
        StateMixin.__init__(self, name)
        ActionStateMixin.__init__(self, on_entry, None)
        CompositeStateMixin.__init__(self)

        self.initial = initial
        self._states = {}  # name -> State object
        self._parent = {}  # name -> parent.name
        self.transitions = []  # list of Transition objects

    def register_state(self, state: StateMixin, parent):
        """
        Register given state. This method also register the given state
        to its parent.

        :param state: state to add
        :param parent: name of its parent
        """
        # Name should be unused so far
        if state.name in self._states.keys():
            raise ValueError('State name {} is already used!'.format(state.name))
        self._states[state.name] = state
        self._parent[state.name] = parent.name if isinstance(parent, StateMixin) else parent

        # Register on parent state
        parent_state = self._states.get(self._parent[state.name], None)
        if parent_state is not None:
            self._states[self._parent[state.name]].children.append(state.name)
        else:
            # ... or on top-level state (self!)
            self.children.append(state.name)

    def register_transition(self, transition: Transition):
        """
        Register given transition and register it on the source state

        :param transition: transition to add
        """
        self.transitions.append(transition)
        self._states[transition.from_state].transitions.append(transition)

    @property
    def states(self):
        """
        A dictionary that associates a state name to a ``StateMixin``
        """
        return self._states

    def events(self, state_or_states=None) -> list:
        """
        List of possible event names.
        If *state_or_states* is omitted, returns all possible event names.
        If *state_or_states* is a string, return the events for which a transition exists
        with a *from_state* equals to given string.
        If *state_or_states* is a list of state names, return the events for all those states.

        :param state_or_states: ``None``, a state name or a list of state names.
        :return: A list of event names
        """
        if state_or_states is None:
            states = self._states.keys()
        elif isinstance(state_or_states, str):
            states = [state_or_states]
        else:
            states = state_or_states

        names = set()
        for transition in self.transitions:
            if transition.event and transition.from_state in states:
                names.add(transition.event.name)
        return sorted(names)

    @lru_cache()
    def ancestors_for(self, state: str) -> list:
        """
        Return an ordered list of ancestors for the given state.
        Ancestors are ordered by decreasing depth.

        :param state: name of the state
        :return: state's ancestors
        """
        ancestors = []
        parent = self._parent[state]
        while parent:
            ancestors.append(parent)
            parent = self._parent[parent]
        return ancestors

    @lru_cache()
    def descendants_for(self, state: str) -> list:
        """
        Return an ordered list of descendants for the given state.
        Descendants are ordered by increasing depth.

        :param state: name of the state
        :return: state's descendants
        """
        descendants = []
        states_to_consider = [state]
        while states_to_consider:
            state = states_to_consider.pop(0)
            state = self._states[state]
            if isinstance(state, CompositeStateMixin):
                for child in state.children:
                    states_to_consider.append(child)
                    descendants.append(child)
        return descendants

    @lru_cache()
    def depth_of(self, state: str) -> int:
        """
        Return the depth of given state (0-indexed).

        :param state: name of the state
        :return: state depth
        """
        if state is None:
            return 0
        ancestors = self.ancestors_for(state)
        return len(ancestors) + 1

    @lru_cache()
    def least_common_ancestor(self, s1: str, s2: str) -> str:
        """
        Return the deepest common ancestor for *s1* and *s2*, or ``None`` if
        there is no common ancestor except root (top-level) state.

        :param s1: name of first state
        :param s2: name of second state
        :return: name of deepest common ancestor or ``None``
        """
        s1_anc = self.ancestors_for(s1)
        s2_anc = self.ancestors_for(s2)
        for state in s1_anc:
            if state in s2_anc:
                return state

    def leaf_for(self, states: list) -> list:
        """
        Considering the list of states names in *states*, return a list containing each
        element of *states* such that this element has no descendant in *states*.
        In other words, this method returns the leaves from the given list of states.

        :param states: a list of names
        :return: the names of the leaves in *states*
        """
        leaves = []
        # TODO: Need a more efficient way to compute this set
        for state in states:
            keep = True
            for descendant in self.descendants_for(state):
                if descendant in states:
                    keep = False
                    break
            if keep:
                leaves.append(state)
        return leaves

    def validate(self) -> bool:
        """
        Validate current statechart:

         - C1. Check that transitions refer to existing states
         - C2. Check that history can only be defined as a child of a CompoundState
         - C3. Check that initial state refer to a parent's child
         - C4. Check that orthogonal states have at least one child
         - C5. Check that there is no internal eventless guardless transition
         - C6. Check that a CompoundState with an incoming transition declares an initial state.

        :return: True if no check fails
        :raise AssertionError: if a check fails
        """
        # C1 & C5
        for transition in self.transitions:
            if (not (transition.from_state in self._states and
                     (not transition.to_state or transition.to_state in self._states))):
                raise AssertionError('C1. Transition {} refers to an unknown state'.format(transition))
            if not transition.event and not transition.guard and not transition.to_state:
                raise AssertionError('C5. Transition {} is an internal, eventless and guardless '
                                     'transition.'.format(transition))

        for name, state in self._states.items():
            if isinstance(state, HistoryState):  # C2
                if not isinstance(self._states.get(self._parent.get(name, None), None), CompoundState):
                    raise AssertionError('C2. History state {} can only be defined in a compound '
                                         '(non-orthogonal) states'.format(state))
                    # Remove because this can be helpful for orthogonal states
                    # if state.initial and not (self._parent[state.initial] == self._parent[name]):
                    #    raise AssertionError('Initial memory of {} should refer to a child of {}'
                    #           .format(state, self._parent[name]))

            if isinstance(state, CompositeStateMixin):  # C4
                if len(state.children) <= 0:
                    raise AssertionError('C4. Composite state {} should have at least one child'.format(state))

            if isinstance(state, CompoundState):  # C3
                if state.initial and not (state.initial in state.children):
                    raise AssertionError('C3. Initial state of {} should refer to one of its children'.format(state))
        if self.initial and not (self.initial in self.children):
            raise AssertionError('C3. Statechart\'s initial state should refer to one of its children')
        # C6
        for transition in self.transitions:
            target_state = self._states.get(transition.to_state, self._states[transition.from_state])
            if isinstance(target_state, CompoundState):
                if not target_state.initial:
                    raise AssertionError('C6. Compound state {} has an incoming transition but does not define an initial state.'.format(target_state))

        return True

    def __repr__(self):
        return 'statechart "{}"'.format(self.name)


class MicroStep:
    """
    Create a micro step. A step consider ``event``, takes ``transition`` and results in a list
    of ``entered_states`` and a list of ``exited_states``.
    Order in the two lists is REALLY important!

    :param event: Event or None in case of eventless transition
    :param transition: a ''Transition`` or None if no processed transition
    :param entered_states: possibly empty list of entered states
    :param exited_states: possibly empty list of exited states
    """

    def __init__(self, event: Event = None, transition: Transition = None,
                 entered_states: list = None, exited_states: list = None):
        self.event = event
        self.transition = transition if transition else []
        self.entered_states = entered_states if entered_states else []
        self.exited_states = exited_states if exited_states else []

    def __repr__(self):
        return 'MicroStep({}, {}, >{}, <{})'.format(self.event, self.transition, self.entered_states, self.exited_states)


class MacroStep:
    """
    A macro step is a list of micro steps.

    :param time: the time at which this step was executed
    :param steps: a list of ``MicroStep`` instances
    """

    def __init__(self, time: int, steps: list):
        self._time = time
        self._steps = steps

    @property
    def steps(self):
        """
        List of micro steps
        """
        return self._steps

    @property
    def time(self):
        """
        Time at which this step was executed.
        """
        return self._time

    @property
    def event(self) -> Event:
        """
        Event (or ``None``) that were consumed.
        """
        for step in self._steps:
            if step.event:
                return step.event
        return None

    @property
    def transitions(self) -> list:
        """
        A (possibly empty) list of transitions that were triggered.
        """
        return [step.transition for step in self._steps if step.transition]

    @property
    def entered_states(self) -> list:
        """
        List of the states names that were entered.
        """
        states = []
        for step in self._steps:
            states += step.entered_states
        return states

    @property
    def exited_states(self) -> list:
        """
        List of the states names that were exited.
        """
        states = []
        for step in self._steps:
            states += step.exited_states
        return states

    def __repr__(self):
        return 'MacroStep@{}({}, {}, >{}, <{})'.format(round(self.time, 3), self.event, self.transitions,
                                                       self.entered_states, self.exited_states)
