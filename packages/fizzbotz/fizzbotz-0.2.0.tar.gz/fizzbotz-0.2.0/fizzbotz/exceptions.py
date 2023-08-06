#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class FizzbotzException(Exception):
    """Base exception for Fizzbotz exceptions."""


class StringLengthError(FizzbotzException):
    """String argument is too long/too short."""


class EmptyStringError(FizzbotzException):
    """String argument is empty."""
