from IptcEditor.src.gui_gtk import NbLayout
from gi.repository import Gtk


def run():
    # run the thang
    window = NbLayout()
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()
    if __name__ == '__main__':
        Gtk.main()

run()
