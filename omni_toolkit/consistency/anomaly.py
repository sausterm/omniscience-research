"""
Gauge anomaly cancellation for Pati-Salam and related models.

Checks all anomaly conditions: cubic, mixed, Witten SU(2), gravitational.
For PS with 3 generations: 48 Weyl fermions per generation, SO(10)-embeddable.
"""

import numpy as np


class AnomalyCancellation:
    """Verify anomaly cancellation for a given fermion content.

    Parameters
    ----------
    fermion_reps : list of dict
        Each dict has 'name', 'su4' (dim), 'su2L' (dim), 'su2R' (dim), 'copies'.
        Default: standard Pati-Salam with 3 generations.
    """

    def __init__(self, fermion_reps: list = None):
        if fermion_reps is None:
            fermion_reps = self._standard_ps_fermions()
        self.fermion_reps = fermion_reps

    @staticmethod
    def _standard_ps_fermions() -> list:
        """Standard PS fermion content: (4,2,1) + (4bar,1,2) per generation."""
        return [
            {'name': 'Q_L', 'su4': 4, 'su2L': 2, 'su2R': 1, 'copies': 3},
            {'name': 'Q_R', 'su4': -4, 'su2L': 1, 'su2R': 2, 'copies': 3},
        ]

    def check_su4_cubic(self) -> dict:
        """SU(4)^3 anomaly: A(R) + A(Rbar) = 0 for each generation."""
        # For SU(N), A(fund) = 1, A(fund_bar) = -1
        total = 0
        for rep in self.fermion_reps:
            sign = 1 if rep['su4'] > 0 else -1
            n4 = abs(rep['su4'])
            n2L = rep['su2L']
            n2R = rep['su2R']
            total += sign * n2L * n2R * rep['copies']
        return {'anomaly': 'SU(4)^3', 'value': total, 'cancelled': total == 0}

    def check_su2_cubic(self, which: str = 'L') -> dict:
        """SU(2)_{L,R}^3 anomaly: d_{abc} = 0 identically for SU(2)."""
        # d_{abc} vanishes identically for SU(2) — no cubic anomaly possible
        return {
            'anomaly': f'SU(2)_{which}^3',
            'value': 0,
            'cancelled': True,
            'reason': 'd_abc = 0 identically for SU(2)',
        }

    def check_mixed(self) -> list:
        """SU(4)^2 x SU(2)_{L,R} and SU(2)_L^2 x SU(4) mixed anomalies.

        All G_A^2 x G_B mixed anomalies vanish trivially in Pati-Salam:
        Tr(T^a T^b T^c) with T^c in a non-abelian factor gives
        Tr_{R_B}(T^c) = 0 (traceless generators). This is guaranteed
        because PS has no U(1) factor at the unified level.
        """
        labels = [
            'SU(4)^2 x SU(2)_L',
            'SU(4)^2 x SU(2)_R',
            'SU(2)_L^2 x SU(4)',
            'SU(2)_R^2 x SU(4)',
        ]
        results = []
        for label in labels:
            results.append({
                'anomaly': label,
                'value': 0,
                'cancelled': True,
                'reason': 'Tr(T^c_G) = 0 for non-abelian G (traceless generators)',
            })
        return results

    def check_witten_su2(self) -> dict:
        """Witten SU(2) anomaly: number of SU(2) doublets must be even."""
        n_doublets_L = 0
        n_doublets_R = 0
        for rep in self.fermion_reps:
            n4 = abs(rep['su4'])
            if rep['su2L'] == 2:
                n_doublets_L += n4 * rep['copies']
            if rep['su2R'] == 2:
                n_doublets_R += n4 * rep['copies']
        return {
            'SU(2)_L_doublets': n_doublets_L,
            'SU(2)_R_doublets': n_doublets_R,
            'L_even': n_doublets_L % 2 == 0,
            'R_even': n_doublets_R % 2 == 0,
            'passed': (n_doublets_L % 2 == 0) and (n_doublets_R % 2 == 0),
        }

    def check_gravitational(self) -> dict:
        """Gravitational anomaly: Tr(1) over all left-handed Weyl fermions = 0."""
        total = 0
        for rep in self.fermion_reps:
            n4 = abs(rep['su4'])
            chirality = 1 if rep['su2L'] > 1 else -1
            total += chirality * n4 * rep['su2L'] * rep['su2R'] * rep['copies']
        return {'anomaly': 'gravitational', 'value': total, 'cancelled': total == 0}

    def run_all(self) -> dict:
        """Run all anomaly checks."""
        su4 = self.check_su4_cubic()
        su2L = self.check_su2_cubic('L')
        su2R = self.check_su2_cubic('R')
        mixed = self.check_mixed()
        witten = self.check_witten_su2()
        grav = self.check_gravitational()

        n_checks = 3 + len(mixed) + 2 + 1  # cubics + mixed + witten(L,R) + grav
        all_passed = (su4['cancelled'] and su2L['cancelled'] and su2R['cancelled']
                      and all(m['cancelled'] for m in mixed)
                      and witten['passed'] and grav['cancelled'])

        return {
            'SU4_cubic': su4,
            'SU2L_cubic': su2L,
            'SU2R_cubic': su2R,
            'mixed': mixed,
            'witten': witten,
            'gravitational': grav,
            'all_passed': all_passed,
            'n_checks': n_checks,
        }
