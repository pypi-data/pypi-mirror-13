import subprocess
import os, magic
from functools import partial


class TagEditor:
    def __init__(self):

        # set up variables
        self.filename = None
        self.directory = None
        self.ftr = []
        self.mode = 'KEY_PHRASES'
        self.accepted_formats = ('image/jpg',
                                 'image/jpeg',
                                 'image/png',
                                 'image/tif',
                                 'image/tiff',
                                 'image/gif')
        # # set up magic method (from imported 'magic' package) to test mime type
        self.mime_check = magic.open(magic.MAGIC_MIME_TYPE)
        self.mime_check.load()

    # set up the directory
    def change_cwd(self):
        if self.directory:
            wd = self.directory.rstrip('/')
            try:
                os.chdir(wd)
                return True
            except FileNotFoundError:
                print('It seems that the directory you entered does not exist!')
        return False

    # # setters & getters
    def set_filename(self, filename=None):
        if filename:
            # if path,
            if '/' in self.my_filter(filename):
                elements = filename.split('/')
                file = self.my_filter(elements.pop())
                path = ''
                for ele in elements:
                    path += self.my_filter(ele) + '/'
                try:
                    os.chdir(path)
                    self.filename = self.my_filter(filename) if filename else None
                    return file
                except FileNotFoundError:
                    print('It seems that the path you entered is incorrect!')
                    return None
            else:
                self.filename = self.my_filter(filename) if filename else None
                return self.my_filter(filename)
        else:
            print('Not operating on single file, as no filename has been set ...')

    def set_directory(self, directory=None):
        self.directory = self.my_filter(directory) if directory else None
        return self.my_filter(directory) if directory else None

    def get_filename(self):
        return self.filename

    def get_directory(self):
        return self.directory

    def set_mode(self, mode=None):
        if mode == 'TAG_TYPES':
            self.mode = 'TAG_TYPES'
        else:
            self.mode = 'KEY_PHRASES'

    def get_tags(self, new_keyphrase_list=None, filename=None):
        if not filename:
            print('No filename submitted!')
        keyphrase_strings_list = []
        tag_type_list = []
        # change to working directory if operating on entire directories
        if self.directory and not self.change_cwd():
            print('Oooops, there has been an error grabbing the keyword tags for {}'.format(filename))
            return False
        # if handling single file, not a directory (and image extension is allowed)
        if not self.directory and self.image_extension_checker(filename):
            if self.mode == 'KEY_PHRASES':
                kp_list = self.generate_keyphrase_list(new_keyphrase_list, filename)
                if kp_list:
                    print('KP LIST DOES EXIST')
                    keyphrase_strings_list.append(kp_list)
                return keyphrase_strings_list or False
            elif self.mode == 'TAG_TYPES':
                if self.generate_tag_type_list():
                    tag_type_list.append(self.generate_tag_type_list()) or False
                return tag_type_list or False
        elif self.directory:
            print('Working on a directory ...')
            file_list = [file for file in os.listdir(os.getcwd()) if os.path.isfile(file)]
            if self.mode == 'KEY_PHRASES':
                for f in file_list:
                    # generate tag list, but only if image extension checker passes
                    more_tags = self.generate_keyphrase_list(new_keyphrase_list, f) \
                        if self.image_extension_checker(f) else None
                    if more_tags:
                        # append a new list inside the tagStringsContainer list containing the file tags
                        keyphrase_strings_list.append([tag for tag in more_tags])
                        # delete the temp holding list values, ready for re-use
                        del more_tags[:]
                return keyphrase_strings_list or False
            elif self.mode == 'TAG_TYPES':
                for f in file_list:
                    more_tags = self.generate_tag_type_list(filename=f) if self.image_extension_checker(f) else None
                    if more_tags:
                        tag_type_list.append([tag for tag in more_tags])
                        del more_tags[:]
                return tag_type_list or False
        else:
            print('Directory is {}\nFilename is {}'.format(os.getcwd(), self.filename))
            return False

    def image_extension_checker(self, filename):
        return True if filename and \
                       self.mime_check.file(filename) in self.get_accepted_formats() else False

    def generate_keyphrase_list(self, new_keyphrase_list, filename):
        tag_strings = []
        # examine the existing IPTC tags1
        try:
            examine = subprocess.Popen(['exiv2', '-PI', filename], stdout=subprocess.PIPE, shell=False)
            output, error = examine.communicate()
        except FileNotFoundError:
            print('It appears that exiv2 may not be installed on your system!')
            return False
        if output:
            # decode the binary output to string
            decoded_output = output.decode()
            # split the string at linebreak, into a list of discrete tags
            tag_list = decoded_output.split('\n')
            # create a list in which to place each element of every tag
            elements_list = []
            ''' loop the tag list and add - to the new elements_list list - NEW lists of tags, split into elements,
            created by splitting the tag string at whitespace (default split())
            elements_list will be a list of lists of elements.
            '''
            for tag in tag_list:
                elements_list.append(tag.split())
            # loop the elements_list (which is a list of lists of elements)
            string_builder = []
            for listOfElements in elements_list:
                if listOfElements and listOfElements[0] == 'Iptc.Application2.Keywords':
                    # append small lists of each element number 3 and above, to the new string_builder list
                    string_builder.append(listOfElements[3:])
            ''' add each complete tag string (elements of stringbuilder joined to string)
            as an element in the new tagStrings list
            '''
            for element in string_builder:
                tag_strings.append(' '.join(element))
            # append the filename to the new list of file tags
            tag_strings.append(filename)
            return tag_strings
        elif not output and new_keyphrase_list:
            # if there was no existing list to add to, but an entirely new list has been set
            print('Adding a new list of keyphrases ...')
            for i in new_keyphrase_list:
                # add items from list of new keyphrases (only 1 now, unless updated to accept additional (delimited)
                # tag_strings.append('Iptc.Application2.Keywords {} {}'.format(len(i), i))
                tag_strings.append(i)
            tag_strings.append(filename)
            # return the new list
            return tag_strings
        else:
            # if no existing tags
            print('No existing IPTC data here ...')
            return False

    def generate_tag_type_list(self, filename):
        tag_types = []
        # examine the existing IPTC tags types
        try:
            examine = subprocess.Popen(['exiv2', '-PI', filename], stdout=subprocess.PIPE, shell=False)
            output, error = examine.communicate()
        except FileNotFoundError:
            print('It appears that exiv2 may not be installed on your system!')
            return False
        if output:
            # decode the binary output to string
            decoded_output = output.decode()
            # split the string at linebreak, into a list of discrete tags
            tag_list = decoded_output.split('\n')
            # create a list in which to place each element of every tag
            elements_list = []
            for tag in tag_list:
                elements_list.append(tag.split())
            # loop the elements_list (which is a list of lists of elements)
            for listOfElements in elements_list:
                if listOfElements:
                    tag_types.append(listOfElements[0])
            tag_types.append(self.filename)
            return tag_types
        else:
            # if no tags
            print('No IPTC data here ...')
            return False

    def replace_keyphrases(self, tag_strings_list=None,
                           new_kp_list=None,
                           working_data=None,
                           tag_to_replace=None,
                           new_tag=None):

        # # FILTERS & SET UP FILENAME/DIRECTORY
        if not working_data:
            print('There does not appear to be a selected data source!')
            return False
        if working_data[0] == 'F':
            self.set_filename(self.my_filter(working_data[1]))
        else:
            self.set_directory(self.my_filter(working_data[1]))
        # filter new keyphrases
        new_keyphrase_list = list(map(self.my_filter, new_kp_list)) if new_kp_list else None
        # filter tag_to_replace
        tag_to_replace = self.my_filter(tag_to_replace)
        # filter new tag
        new_tag = self.my_filter(new_tag)
        # filter tag_strings_list
        tag_strings_list = list(map(self.filter_taglist, tag_strings_list)) if tag_strings_list else None

        # # WORK
        if tag_strings_list:
            for tag_list in tag_strings_list:
                if tag_list:
                    # get filename associated with each tag_list
                    f = tag_list.pop()
                    if tag_to_replace in tag_list:
                        # replace old string with new
                        for num, s in enumerate(tag_list):
                            if s == tag_to_replace:
                                print('Being replaced!')
                                if not new_tag:
                                    # if no new tag, just delete the old
                                    del tag_list[num]
                                else:
                                    # replace the old tag with the new
                                    tag_list[num] = new_tag
                        # delete the old strings
                        subprocess.call(['exiv2', '-M', 'del Iptc.Application2.Keywords', f],
                                        stdout=subprocess.PIPE, shell=False)
                        # add the new strings and remove dupes just for good measure!
                        no_dupes = self.remove_dupes(tag_list)
                        if no_dupes:
                            for tag in no_dupes:
                                print('Replacing with: ', tag)
                                subprocess.call(
                                    ['exiv2', '-M', 'add Iptc.Application2.Keywords String {0}'.format(tag), f],
                                    stdout=subprocess.PIPE, shell=False)
                            print('Job done! The new tags for {0} are: '.format(f), tag_list)
                    elif not tag_to_replace and new_keyphrase_list:
                        # iterate new keyphrase list and pass each value to the add_tag method, using MAP.
                        list(map(partial(self.add_tag, f), new_keyphrase_list))
                    else:
                        print('Dinae change ... the current tags for {0} are: '.format(f), tag_list)
                else:
                    # if tag list is empty (i.e. there no existing tags)
                    subprocess.call(
                        ['exiv2', '-M', 'add Iptc.Application2.Keywords String {0}'.
                            format(new_tag), self.filename],
                        stdout=subprocess.PIPE, shell=False)
                    print('Job done! The new tags for {0} are: '.format(self.filename), tag_list)
        else:
            print('There were no tags submitted!')
            return False

    def filter_taglist(self, tag_list):
        return list(map(self.my_filter, tag_list)) if tag_list else None

    def add_tag(self, filename, tag):
        subprocess.call(['exiv2', '-M', 'add Iptc.Application2.Keywords String {0}'.format(tag), filename],
                        stdout=subprocess.PIPE, shell=False)
        return 'Tag {} added to {}.'.format(tag, filename)

    def remove_exif_field(self, field_to_remove):
        if field_to_remove:
            # if scanning a directory
            if self.directory:
                wd = self.directory.rstrip('/')
                os.chdir(wd)
                file_list = [file for file in os.listdir(wd) if os.path.isfile(file)]
                for f in file_list:
                    for field in field_to_remove:
                        subprocess.call(['exiv2', '-M', 'del {0}'.format(field), f],
                                        stdout=subprocess.PIPE, shell=False)
                        print('If field "{0}" did exist in {1}, it disnae now!'.format(field, f))
                # # clear fields to remove list
                del self.ftr[:]
                return True
            # if a single file
            elif self.filename and not self.directory:
                for field in field_to_remove:
                    subprocess.call(['exiv2', '-M', 'del {0}'.format(field), self.filename],
                                    stdout=subprocess.PIPE, shell=False)
                    print('Field {0} removed!'.format(field))
                    # # clear field to remove
                del self.ftr[:]
                return True
            else:
                return False

    def get_accepted_formats(self):
        return self.accepted_formats

    @staticmethod
    def remove_dupes(tag_list=None):
        discrete = set()
        no_dupes = []
        if tag_list:
            for tag in tag_list:
                if tag not in discrete:
                    no_dupes.append(tag)
                discrete.add(tag)
        return no_dupes

    @staticmethod
    def my_filter(incoming=None):
        if incoming is not None:
            # sanitize the strings
            extra_chars = [':', '.', ' ', '|', '-', '~', '*', '/', '\[', '\]', '!', '_']
            return ''.join([c if c.isalnum() or c in extra_chars else '' for c in incoming])
        else:
            return None  # get the inputs
