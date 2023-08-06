#!/usr/bin/env python3
"""
This module provides classes that can be used to evaluate math expression contained in string.
Most common class is Ncalc. It allows you evaluate expression contains variables 'x', 'y' and most common
functions such as sin, cos, tg, log2, log10, exp, mod, exp and factorial.
Furthermore you can build your own 'calculator' with your own operator precedences
(don't know why it can be need), functions and variables.
To build The Calculator see at Ncalc definition and do it like it:
    1. Define new class inherited from Matheval:

class Ncalc(Matheval):

    2. Using __init__ set up given math expression and context namely dictionary of variables and functions:

    def __init__(self, mexp):
        super().__init__(mexp, {
            'x': 1,
            'y': 1,
            'factorial': Ncalc.__factorial,
        })

    3. Wrap functions as 'staticmethod' or functions of module:

    @staticmethod
    def __log10(a):
        return math.log10(a)

    4. That's it. :)

P.S. This version can work wrong cause I didn't test it as it's necessary.
"""
__author__ = 'Artem Yaschenko'
__copyright__ = 'Copyright 2016, Ncalc project'
__license__ = 'GPL'
__version__ = '0.7'
__maintainer__ = 'Artem Yaschenko'
__email__ = 'ayaschenko@yahoo.com, algolc@gmail.com'

import types
import math


def top(stack):
    return stack[len(stack) - 1]


class Matheval(object): # main class converts expression to postfix notation
    # defines precedences of operators
    precedences = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
        '^': 3,
        '(': 0,
    }

    def __init__(self, strmathexp, context = {}):
        self.precedences = Matheval.precedences
        self.rawexp = strmathexp
        self.context = context # contains variables and functions used for evaluating
        self.postfixexp = ''
        self.__conversion() # convert 'strmathexp' to postfix

    def __conversion(self): # convert to postfix
        delimfound = False # mean '.' has not found
        identif = False # mean current token is variable or function name
        operand = '' # current token
        caret = 1 # current position

        stack = [] # stack of operators
        i = 0
        while i < len(self.rawexp):
            c = self.rawexp[i]
            i += 1
            if (c.isdigit() or (c == '.' and not delimfound)) and not identif:
                if c == '.':
                    delimfound = True
                operand += c
            elif c.isalpha() and not identif and operand == '':
                identif = True
                operand += c
            elif (c.isalpha() or c.isdigit()) and identif:
                operand += c
            elif c == '(':
                if identif: # function caught))
                    # evaluate arguments,
                    # push it before function name,
                    # then push function name
                    tpars = 1 # mean that not all arguments read (must be 0)
                    fargs = []
                    while tpars != 0:
                        arg = ''
                        c = self.rawexp[i] # after '('
                        while i < len(self.rawexp):
                            c = self.rawexp[i]
                            if c == '(':
                                tpars += 1
                            elif c == ')':
                                tpars -= 1
                            if (c == ',' and tpars == 1) or (c == ')' and tpars == 0):
                                break
                            arg += c
                            i += 1
                        innerexp = Matheval(arg, self.context).eval()
                        fargs.append(innerexp)
                        i += 1
                    # ready to go to stack
                    while len(fargs) > 0:
                        self.postfixexp += str(fargs.pop()) + ' '
                else:
                    if operand != '':
                        self.postfixexp += operand + ' '
                    delimfound, identif, operand = (False, False, '')
                    stack.append(c)
            elif c == ')':
                self.postfixexp += operand + ' '
                delimfound, identif, operand = (False, False, '')
                if top(stack) == '(':
                    raise Exception('Wrong parentheses order at ' + str(caret))
                try:
                    while top(stack) != '(':
                        self.postfixexp += stack.pop() + ' '
                except:
                    raise Exception('Wrong parentheses order (was not opened) at ' + str(caret))
                else:
                    stack.pop() # pop last '('
            elif c in self.precedences:
                self.postfixexp += operand + ' '
                delimfound, identif, operand = (False, False, '')
                if self.postfixexp == '': # operand == ''
                    raise Exception('Wrong character at ' + str(caret))
                if len(stack) == 0:
                    stack.append(c)
                else:
                    while len(stack) > 0 and self.precedences[top(stack)] >= self.precedences[c]:
                        self.postfixexp += stack.pop() + ' '
                    stack.append(c)
            else:
                if c.isspace():
                    pass
                else:
                    raise Exception('Wrong character at ' + str(caret))
            caret += 1
        if operand != '':
            self.postfixexp += operand + ' '
        while len(stack) > 0:
            self.postfixexp += stack.pop() + ' '

    @staticmethod
    def numfrom(sval):
        if sval.isdigit():
            return int(sval)
        else:
            v = None
            try:
                v = float(sval)
            except:
                #raise ValueError(sval + ': str cant be converted to num')
                return None
            else:
                return v

    def eval(self):
        stack = []
        sexp = self.postfixexp.split(' ')
        for i in sexp:
            if Matheval.numfrom(i) != None:
                stack.append(Matheval.numfrom(i))
            elif i.isalpha():
                if i not in self.context:
                    raise Exception(i + ' - undefined identifier.')
                if isinstance(self.context[i], types.FunctionType):
                    argcount = self.context[i].__code__.co_argcount
                    args = []
                    while argcount > 0:
                        try:
                            a = stack.pop()
                        except:
                            raise Exception('Wrong number of arguments to ' + i)
                        args.append(a)
                        argcount -= 1
                    stack.append(self.context[i](*args))
                else:
                    stack.append(self.context[i])
            elif i == '*':
                o1 = stack.pop()
                o2 = stack.pop()
                stack.append(o1 * o2)
            elif i == '/':
                o1 = stack.pop()
                o2 = stack.pop()
                stack.append(o2 / o1)
            elif i == '+':
                o1 = stack.pop()
                o2 = stack.pop()
                stack.append(o1 + o2)
            elif i == '-':
                o1 = stack.pop()
                o2 = stack.pop()
                stack.append(o2 - o1)
            elif i == '^':
                o1 = stack.pop()
                o2 = stack.pop()
                stack.append(o2 ** o1)
        return stack.pop()

    def __getattribute__(self, item):
        if item == 'expression':
            return self.rawexp
        else: return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        if key == 'expression':
            self.rawexp = value
            self.__conversion()
        else:
            object.__setattr__(self, key, value)

    def __str__(self):
        return '<{0}: "{1}">'.format(self.__class__.__name__, self.rawexp, self.postfixexp)


class Ncalc(Matheval):
    def __init__(self, mexp):
        # defines 'default' context that contains the most common functions and 2 variable
        super().__init__(mexp, {
            'x': 1,
            'y': 1,
            'factorial': Ncalc.__factorial,
            'exp': Ncalc.__exp,
            'log2': Ncalc.__log2,
            'mod': Ncalc.__mod,
            'sin': Ncalc.__sin,
            'cos': Ncalc.__cos,
            'tg': Ncalc.__tg,
            'log10': Ncalc.__log10,
        })

    @staticmethod
    def __log10(a): # built-in functions doesn't work (don't know why, cause it different type???), so it must be ordinary function or method
        return math.log10(a)

    @staticmethod
    def __factorial(a): # just wrap it
        return math.factorial(a)

    @staticmethod
    def __exp(a):
        return math.exp(a)

    @staticmethod
    def __log2(a):
        return math.log2(a)

    @staticmethod
    def __mod(a, b):
        return a % b

    @staticmethod
    def __sin(a):
        return math.sin(a)

    @staticmethod
    def __cos(a):
        return math.cos(a)

    @staticmethod
    def __tg(a):
        return math.tan(a)


if __name__ == '__main__':
    fc = Ncalc('5-x*y')
    print(fc)
    print(fc.eval())
    fc.expression = 'factorial(5)'
    print(fc.eval())
    fc.expression = 'exp(2)*120'
    print(fc.eval())
    e1 = Ncalc('sin(0.75)')
    e2 = Ncalc('cos(0.75)')
    e3 = Ncalc('tg(0.75)')
    e4 = Ncalc('sin(0.75)/cos(0.75)')
    print('{0:.3f} = {1:.3f}/{2:.3f} = {3:.3f}'.format(e3.eval(), e1.eval(), e2.eval(), e4.eval()))
    e = Ncalc('mod(5, 2)')
    print(e.eval())
