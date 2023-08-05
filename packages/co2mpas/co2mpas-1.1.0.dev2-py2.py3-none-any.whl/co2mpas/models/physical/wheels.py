#-*- coding: utf-8 -*-
#
# Copyright 2015 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

"""
It provides a wheels model.

The model is defined by a Dispatcher that wraps all the functions needed.
"""


from co2mpas.dispatcher import Dispatcher
from co2mpas.functions.physical.wheels import *
import co2mpas.dispatcher.utils as dsp_utl


def wheels():
    """
    Defines the wheels model.

    .. dispatcher:: dsp

        >>> dsp = wheels()

    :return:
        The wheels model.
    :rtype: Dispatcher
    """

    wheels = Dispatcher(
        name='Wheel model',
        description='It models the wheel dynamics.'
    )

    wheels.add_function(
        function=calculate_wheel_torques,
        inputs=['wheel_powers', 'wheel_speeds'],
        outputs=['wheel_torques']
    )

    wheels.add_function(
        function=calculate_wheel_powers,
        inputs=['wheel_torques', 'wheel_speeds'],
        outputs=['wheel_powers']
    )

    wheels.add_function(
        function=calculate_wheel_speeds,
        inputs=['velocities', 'r_dynamic'],
        outputs=['wheel_speeds']
    )

    wheels.add_function(
        function=identify_r_dynamic,
        inputs=['velocity_speed_ratios', 'gear_box_ratios',
                'final_drive_ratio'],
        outputs=['r_dynamic']
    )

    wheels.add_function(
        function=identify_r_dynamic_v1,
        inputs=['velocities', 'gears', 'engine_speeds_out', 'gear_box_ratios',
                'final_drive_ratio'],
        outputs=['r_dynamic'],
        weight=10
    )

    wheels.add_function(
        function=calculates_brake_powers,
        inputs=['engine_moment_inertia', 'motive_powers', 'gear_box_speeds_in',
                'auxiliaries_torque_losses', 'has_energy_recuperation',
                'alternator_nominal_power'],
        outputs=['brake_powers']
    )

    wheels.add_function(
        function=calculates_brake_powers,
        inputs=['engine_moment_inertia', 'motive_powers', 'gear_box_speeds_in',
                'auxiliaries_torque_losses'],
        outputs=['brake_powers'],
        weight=50
    )

    wheels.add_function(
        function=dsp_utl.summation,
        inputs=['motive_powers', 'brake_powers'],
        outputs=['wheel_powers']
    )

    return wheels
