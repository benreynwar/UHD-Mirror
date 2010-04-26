#!/usr/bin/env python
#
# Copyright 2010 Ettus Research LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
from common import *

########################################################################
# Template for raw text data describing registers
# name addr[bit range inclusive] default optional enums
########################################################################
REGS_DATA_TMPL="""\
########################################################################
## Note: offsets given from perspective of data bits (excludes address)
########################################################################
##
########################################################################
## Standby (2)
########################################################################
_set_to_1_2_0         2[0]          1
_set_to_1_2_1         2[1]          1
_set_to_1_2_2         2[2]          1
pa_bias_dac           2[10]         0
voltage_ref           2[11]         0
_set_to_1_2_12        2[12]         1
mimo_select           2[13]         0                 normal, mimo
########################################################################
## Integer Divider Ratio (3)
########################################################################
int_div_ratio_word    3[0:7]        a2
frac_div_ratio_lsb    3[12:13]      0
########################################################################
## Fractional Divider Ratio (4)
########################################################################
frac_div_ratio_msb    4[0:13]       0
########################################################################
## Band Select and PLL (5)
########################################################################
band_select           5[0]          0                 2_4ghz, 5ghz
ref_divider           5[1:3]        1
pll_cp_select         5[5]          1                 2ma, 4ma
band_select_802_11a   5[6]          0                 4_9ghz_to_5_35ghz, 5_47ghz_to_5_875ghz
vco_bandswitch        5[7]          0                 disable, automatic
vco_spi_bandswitch    5[8]          0                 fsm, spi
vco_sub_band          5[9:10]       0
_set_to_1_5_11        5[11]         1
_set_to_1_5_12        5[12]         1
band_sel_mimo         5[13]         0                 normal, mimo
########################################################################
## Calibration (6)
########################################################################
rx_cal_mode           6[0]          0                 dis, enb
tx_cal_mode           6[1]          0                 dis, enb
_set_to_1_6_10        6[10]         1
iq_cal_gain           6[11:12]      3                 8db, 18db, 24db, 34db
########################################################################
## Lowpass Filter (7)
########################################################################
rx_lpf_fine_adj       7[0:2]        2                 90, 95, 100, 105, 110
rx_lpf_coarse_adj     7[3:4]        1                 7_5mhz, 9_5mhz, 14mhz, 18mhz
tx_lpf_coarse_adj     7[5:6]        1                 12mhz=1, 18mhz=2, 24mhz=3
rssi_high_bw          7[11]         0                 2mhz, 6mhz
########################################################################
## Rx Control/RSSI (8)
########################################################################
_set_to_1_8_0         8[0]          1
rx_highpass           8[2]          1                 100hz, 30khz
_set_to_1_8_5         8[5]          1
rssi_pin_fcn          8[8]          0                 rssi, temp
rssi_op_mode          8[10]         0                 rssi_rxhp, enabled
rssi_output_range     8[11]         0                 low, high
rx_vga_gain_spi       8[12]         0                 io, spi
########################################################################
## Tx Linearity/Baseband Gain (9)
########################################################################
tx_baseband_gain      9[0:1]        0                 0db, 2db, 3_5db, 5db
tx_upconv_linearity   9[2:3]        0                 50, 63, 78, 100
tx_vga_linearity      9[6:7]        0                 50, 63, 78, 100
pa_driver_linearity   9[8:9]        2                 50, 63, 78, 100
tx_vga_gain_spi       9[10]         0                 io, spi
########################################################################
## PA Bias DAC (10)
########################################################################
pa_bias_dac_out_curr  a[0:5]        0
pa_bias_dac_delay     a[6:9]        f
########################################################################
## Rx Gain (11)
########################################################################
rx_vga_gain           b[0:4]        1f
rx_lna_gain           b[5:6]        3
########################################################################
## Tx VGA Gain (12)
########################################################################
tx_vga_gain           c[0:5]        0
"""

########################################################################
# Header and Source templates below
########################################################################
HEADER_TEXT="""
#import time

/***********************************************************************
 * This file was generated by $file on $time.strftime("%c")
 **********************************************************************/

\#ifndef INCLUDED_MAX2829_REGS_HPP
\#define INCLUDED_MAX2829_REGS_HPP

\#include <boost/cstdint.hpp>

struct max2829_regs_t{
#for $reg in $regs
    #if $reg.get_enums()
    enum $(reg.get_name())_t{
        #for $i, $enum in enumerate($reg.get_enums())
        #set $end_comma = ',' if $i < len($reg.get_enums())-1 else ''
        $(reg.get_name().upper())_$(enum[0].upper()) = $enum[1]$end_comma
        #end for
    } $reg.get_name();
    #else
    boost::$reg.get_stdint_type() $reg.get_name();
    #end if
#end for

    max2829_regs_t(void){
#for $reg in $regs
        $reg.get_name() = $reg.get_default();
#end for
    }

    boost::uint32_t get_reg(boost::uint8_t addr){
        boost::uint16_t reg = 0;
        switch(addr){
        #for $addr in range(2, 12+1)
        case $addr:
            #for $reg in filter(lambda r: r.get_addr() == addr, $regs)
            reg |= (boost::uint16_t($reg.get_name()) & $reg.get_mask()) << $reg.get_shift();
            #end for
            break;
        #end for
        }
        return (boost::uint32_t(reg) << 4) | (addr & 0xf);
    }
};

\#endif /* INCLUDED_MAX2829_REGS_HPP */
"""

if __name__ == '__main__':
    regs = map(reg, parse_tmpl(REGS_DATA_TMPL).splitlines())
    open(sys.argv[1], 'w').write(parse_tmpl(HEADER_TEXT, regs=regs, file=__file__))