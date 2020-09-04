    def item_matches(text, field_name, item):
        """ Counts the number of occurrences of item in text

        """
        options = item_analysis[field_name]
        separator = options.get('separator', ' ')
        regexp = options.get('separator_regexp')
        if regexp is None:
            regexp = r"%s" % re.escape(separator)
        return count_items_matches(text, item, regexp)


    def count_items_matches(text, item, regexp):
        """ Counts the number of occurrences of the item in the text

        """
        expression = r'(^|%s)%s($|%s)' % (regexp, item, regexp)
        pattern = re.compile(expression, flags=re.U)
        matches = re.findall(pattern, text)
        return len(matches)
