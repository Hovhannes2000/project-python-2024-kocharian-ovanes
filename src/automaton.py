class NFA:
    def __init__(self, states=None, alphabet=None, transition_function=None, 
                 initial_state=None, final_states=None):
        self.is_single_letters = False
        self.is_without_epsilon = False
        self.is_dfa = False
        self.is_full_dka = False
        
        if states is None:
            self.states = []  # Пустой список состояний
        else:
            self.states = states

        if alphabet is None:
            self.alphabet = set()  # Пустой алфавит
        else:
            self.alphabet = alphabet

        if transition_function is None:
            self.transition_function = {}  # Пустой словарь переходов
        else:
            self.transition_function = transition_function

        if initial_state is None:
            self.initial_state = None  # Нет начального состояния
        else:
            self.initial_state = initial_state

        if final_states is None:
            self.final_states = set()  # Пустой набор конечных состояний
        else:
            self.final_states = final_states

    #######################################################################

    def make_transitions_single_letter(self):
        new_transition_function = {}
        new_states_count = len(self.states)
        new_states = self.states.copy()  # Сохраняем оригинальные состояния

        for (state, symbol), next_state in self.transition_function.items():
            if len(symbol) > 1:  # Если символ многосимвольный
                for all_states in next_state:
                    current_state = state
                    for char in symbol[:-1]:  # Проходим через каждый символ кроме последней
                        next_state_name = f'q{new_states_count}'
                        new_states.append(next_state_name)
                        # Добавляем переход от текущего состояния к следующему по одному символу
                        new_transition_function.setdefault((current_state, char), set()).add(next_state_name)
                        current_state = next_state_name
                        new_states_count += 1
                    # Последним символом соединяем с all_state
                    char = symbol[-1]
                    new_transition_function.setdefault((current_state, char), set()).add(all_states)
            else:  # Однобуквенный символ
                if (state, symbol) not in new_transition_function:
                    new_transition_function[(state, symbol)] = next_state

        self.states = new_states
        self.transition_function = new_transition_function
        self.is_single_letters = True

    #######################################################################

    def rename_dfa_states(self):
        # Переименовывает состояния DFA в более читаемый формат убирая frozenset.
        new_states = {}
        new_transition_function = {}

        # Обходим каждое состояние DFA и создаем новое имя для него
        for index, state in enumerate(self.states):
            new_name = f'q{index}'
            new_states[tuple(state)] = new_name  # Переименовываем с использованием tuple вместо frozenset

        # Обновляем функцию переходов с новыми именами
        for (curr_state, symbol), next_state in self.transition_function.items():
            curr_state_name = new_states[tuple(curr_state)]
            next_state_name = new_states[tuple(next_state)]
            new_transition_function[(curr_state_name, symbol)] = {next_state_name}

        # Обновляем начальное и финальные состояния

        new_initial_state = new_states[tuple(self.initial_state)]
        new_final_states = {new_states[tuple(f)] for f in self.final_states}
        
        self.states = list(new_states.values())
        self.alphabet = self.alphabet
        self.transition_function = new_transition_function
        self.initial_state = new_initial_state
        self.final_states = list(new_final_states)

    #######################################################################

    def remove_epsilon_transitions(self):
        # Пустой переход будем считать переходом по символу '1'
        # Переводим НКА в НКА с однобуквенными переходами
        if not self.is_single_letters:
            self.make_transitions_single_letter()

        new_transition_function = {}
        # Копирую все переходы в new_transition_function
        for state in self.states:
            for symbol in self.alphabet:
                if (state, symbol) in self.transition_function:
                    new_transition_function[(state, symbol)] = self.transition_function[(state, symbol)].copy()

        for state in self.states:
            while (state, '1') in self.transition_function:
                for next_state in new_transition_function[(state, '1')]:
                    next_states = new_transition_function[(state, '1')].copy()
                    for symbol in self.alphabet:
                        if (next_state, symbol) in new_transition_function:
                            if (state, symbol) not in self.transition_function:
                                self.transition_function[(state, symbol)] = set()
                            copy = new_transition_function[(next_state, symbol)].copy()
                            self.transition_function[(state, symbol)] |= copy
                self.transition_function[(state, '1')] -= next_states
                new_transition_function.pop((state, '1'), None)
                if not self.transition_function[(state, '1')]:
                    self.transition_function.pop((state, '1'), None)
                if (state, '1') in self.transition_function:
                    if (state, '1') not in new_transition_function:
                        new_transition_function[(state, '1')] = set()
                    copy = self.transition_function[(state, '1')].copy()
                    new_transition_function[(state, '1')] |= copy

        # Убираю из алфавита пустой переход
        while '1' in self.alphabet:
            self.alphabet.remove('1')

        self.is_without_epsilon = True

#######################################################################

    def nfa_to_dfa(self):
        # Преобразует NFA без ε-переходов в эквивалентный DFA.
        if not self.is_without_epsilon:
            self.remove_epsilon_transitions()
            
        dfa_states = []
        dfa_transition_function = {}
        dfa_final_states = set()

        # Начальное состояние DFA - это состояние начального состояния NFA
        initial_state = frozenset([self.initial_state])
        dfa_states.append(initial_state)

        # Используем очередь для обхода состояний DFA
        queue = [initial_state]

        while queue:
            current_states = queue.pop(0)

            # Проверяем каждый символ алфавита NFA
            for symbol in self.alphabet:
                # Находим все состояния, которые можно достичь из current_states по символу
                next_states = move(current_states, symbol, self.transition_function)

                if next_states:
                    sorted(next_states)
                    next_state_frozen = frozenset(next_states)

                    # Добавляем новый набор состояний, если его еще нет в DFA
                    if next_state_frozen not in dfa_states:
                        dfa_states.append(next_state_frozen)
                        queue.append(next_state_frozen)

                    # Добавляем переход в DFA
                    dfa_transition_function[(current_states, symbol)] = next_state_frozen

            # Проверяем, является ли текущее состояние финальным
            if any(state in self.final_states for state in current_states):
                dfa_final_states.add(current_states)

        # Меняем в DFA

        self.states = [set(s) for s in dfa_states]
        self.transition_function = dfa_transition_function.copy()
        self.initial_state = initial_state
        self.final_states = dfa_final_states.copy()
        self.is_dfa = True
        self.rename_dfa_states()

#######################################################################

    def fulling_dfa(self):
        # ДКА переводит в ПДКА
        # Если не ДКА, переводит в ДКА
        if not self.is_dfa:
            self.nfa_to_dfa()
        
        # Добавляем состояние TRASH
        if 'TRASH' not in self.states:
            self.states.append('TRASH')
        
        # Добавляем переходы по всем буквам
        for state in self.states:
            for symbol in self.alphabet:
                if (state, symbol) not in self.transition_function:
                    self.transition_function.setdefault((state, symbol), set()).add('TRASH')
        
        self.is_full_dka = True

############################################################################################################

def move(states, symbol, transition_function):
    # Находит все состояния, которые можно достичь из множества состояний по символу.
    if isinstance(states, str):
        states_in_set = set()
        states_in_set.add(states)
    else:
        states_in_set = states 

    result = set()
    for state in states_in_set:
        if (state, symbol) in transition_function:
            result.update(transition_function[(state, symbol)])
    
    return result
