            self.MISSING_TOKENS = ['?']
        except Exception, exc:
            sys.stderr.write(\"Cannot read csv\"
                             \" input. %s\\n\" % str(exc))

    def __iter__(self):
        """ Iterator method

        """
        return self

    def next(self):
        """ Returns processed data in a list structure

        """
        def normalize(value):
            """Transforms to unicode and cleans missing tokens
            """
            value = unicode(value.decode('utf-8'))
            return \"\" if value in self.MISSING_TOKENS else value

        def cast(function_value):
            """Type related transformations
            """
            function, value = function_value
            if not len(value):
                return None
            if function is None:
                return value
            else:
                return function(value)

        try:
            values = self.reader.next()
        except StopIteration:
            raise StopIteration()
        if len(values) < len(self.INPUT_FIELDS):
            sys.stderr.write(\"Found %s fields when %s were expected.\\n\" %
                             (len(values), len(self.INPUT_FIELDS)))
            raise StopIteration()
        else:
            values = values[0:len(self.INPUT_FIELDS)]
        try:
            values = map(normalize, values)
            for key in self.PREFIXES:
                prefix_len = len(self.PREFIXES[key])
                if values[key][0:prefix_len] == self.PREFIXES[key]:
                    values[key] = values[key][prefix_len:]
            for key in self.SUFFIXES:
                suffix_len = len(self.SUFFIXES[key])
                if values[key][-suffix_len:] == self.SUFFIXES[key]:
                    values[key] = values[key][0:-suffix_len]
            function_tuples = zip(self.INPUT_TYPES, values)
            values = map(cast, function_tuples)
            data = {}
            for i in range(len(values)):
                data.update({self.INPUT_FIELDS[i]: values[i]})
            return data
        except Exception, exc:
            sys.stderr.write(\"Error in data transformations. %s\\n\" % str(exc))
            return False
\n\n
