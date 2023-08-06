import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.lang import Builder
from kivy.core.clipboard import CutBuffer, Clipboard
from kivy.config import Config

from ConfigParser import NoOptionError


try:
	mouse = Config.get('input', 'mouse')
except NoOptionError:
	pass
else:
	Config.set('input', 'mouse', mouse + ',disable_multitouch')


root = Builder.load_string('''
<SLabel@Label>:
	size_hint_y: None
	height: self.texture_size[1] + dp(12)

<Buttons@BoxLayout>:
	size_hint_y: None
	height: dp(32)

BoxLayout:
	orientation: 'vertical'

	BoxLayout:
		spacing: dp(4)
		padding: dp(4)

		BoxLayout:
			orientation: 'vertical'

			SLabel:
				id: reference
				text: 'Source'
			TextInput:
				id: source
				multiline: True
				on_text: app.apply_manip()
			Buttons:
				Button:
					text: 'Clear'
					on_release: app.clear_source()
				Button:
					text: 'Paste'
					on_release: app.paste_clipboard()
				Button:
					id: cutbuffer
					text: 'Buffer'
					on_release: app.paste_cutbuffer()

		BoxLayout:
			orientation: 'vertical'

			SLabel:
				text: 'Output'
			RelativeLayout:
				TextInput:
					id: output
					readonly: True
					multiline: True
					valid: False
					background_color: (1, 1, 1, 1) if self.valid else (1, 1, 1, 0.6)
				SLabel:
					id: error
					pos_hint: {'y': 0}
					text_size: self.width - dp(10), None
					color: 1, 0.2, 0.3, 1

					canvas.before:
						Color:
							rgba: 1, 1, 1, (0.8 if self.text else 0)
						Rectangle:
							pos: self.pos
							size: self.size
			Buttons:
				Button:
					text: 'Copy'
					on_release: app.copy_output()
				Button:
					text: 'Copy and Exit'
					on_release: app.copy_and_exit()

	TextInput:
		id: manip
		size_hint_y: None
		height: reference.height * 3.0
		text: 's'
		on_text: app.apply_manip()
		valid: False
		background_color: (1, 1, 1, 1) if self.valid else (1, 0.8, 0.8, 1)
''')


class StrManipApp(App):
	def build(self):
		return root

	def on_start(self):
		text = ''
		if CutBuffer:
			text = CutBuffer.get_cutbuffer()
		else:
			cbbtn = root.ids.cutbuffer
			cbbtn.parent.remove_widget(cbbtn)
		if not text:
			text = Clipboard.copy()
		root.ids.source.text = text or ''
		root.ids.manip.focus = True

	def apply_manip(self):
		source = root.ids.source.text
		manip = root.ids.manip.text

		try:
			output = eval(manip, {}, {'s': source})
			if not isinstance(output, basestring):
				try:
					output = '\n'.join(output)
				except Exception:
					raise Exception('output is not a string or iterable')
		except Exception as e:
			root.ids.manip.valid = False
			root.ids.output.valid = False
			root.ids.error.text = str(e)
		else:
			root.ids.manip.valid = True
			root.ids.output.text = ''
			root.ids.output.text = output
			root.ids.output.valid = True
			root.ids.error.text = ''

	def clear_source(self):
		root.ids.source.text = ''

	def paste_clipboard(self):
		root.ids.source.text = Clipboard.paste()

	def paste_cutbuffer(self):
		root.ids.source.text = CutBuffer.get_cutbuffer()

	def copy_output(self):
		Clipboard.copy(root.ids.output.text)
		if CutBuffer:
			CutBuffer.set_cutbuffer(root.ids.output.text)

	def copy_and_exit(self):
		self.copy_output()
		self.stop()


if __name__ == '__main__':
	StrManipApp().run()
