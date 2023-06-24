HEX_FILE=stk500boot_v2_mega2560.hex

# Avrdude configuration to connect on the PI. See avrdude_gpio.conf.
# Can be one of: pi_rst, pi_cs0, pi_cs1 or pi_gpio, depending on the RESET line in AVR.
AVRDUDE_CONFIG=pi_rst

# AVR fuses: external crystal (see https://www.engbedded.com/fusecalc/)
FUSES=-U lfuse:w:0xff:m -U hfuse:w:0xd8:m -U efuse:w:0xfd:m

# Microcontroller
MCU_AVRDUDE=atmega2560

# Microcontroller speed, in Hz. Used by avr-libc for delays.
F_CPU=16000000UL

AVRDUDE_FLAGS=-p ${MCU_AVRDUDE} -C +./avrdude_gpio.conf -c ${AVRDUDE_CONFIG} -V

test-connection:
	sudo avrdude ${AVRDUDE_FLAGS}

upload: ${HEX_FILE}
	sudo avrdude ${AVRDUDE_FLAGS} -U flash:w:$<:i

fuse:
	sudo avrdude ${AVRDUDE_FLAGS} ${FUSES}

# vim: set ts=8 sts=8 sw=8 noexpandtab:
