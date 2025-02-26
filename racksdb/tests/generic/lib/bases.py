# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later


class TestAppleCrateBase:
    def _filter(self, quantity_min=None):
        if quantity_min and quantity_min > self.quantity:
            return False
        return True


class TestAppleBase:
    def _filter(self, color=None):
        if color and color != self.color:
            return False
        return True
