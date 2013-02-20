value_ok = '<img src="/tpl/images/ok.png" />'
value_not_ok = '<img src="/tpl/images/not_ok.png" />'

def ok_icon(value):
        if value:
                return value_ok
        else:
                return value_not_ok

def format_signal_level(value):
	if value is False:
		level = '00'
	elif value < 50:
		level = '100'
	elif value < 100:
		level = '75'
	elif value < 200:
		level = '50'
	else:
		level = '25'
	return '<img src="/tpl/images/nm-signal-%s.png" title="%s ms" />' % (level, value)


def format_ping(value):
	if not value:
		return format_signal_level(False)
	else:
		return format_signal_level(int(value*1000))


