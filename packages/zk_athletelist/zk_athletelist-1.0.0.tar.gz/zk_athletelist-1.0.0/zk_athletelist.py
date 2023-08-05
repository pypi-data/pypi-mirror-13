def sanitize(time_string):
    if "-" in time_string:
        spitter = "-"
    elif ":" in time_string:
        spitter = ":"
    else:
        return time_string
    (mis, sec) = time_string.split(spitter)
    return (mis + "." + sec)

class AthleteList(list):
    def __init__(self, a_name, a_birthday = None, a_times = []):
        list.__init__([])
        self.name = a_name
        self.birthday = a_birthday
        self.extend(a_times)

    def top3(self):
        return (sorted(set(sanitize(t) for t in self))[0:3])