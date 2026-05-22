from fontquant._fontquant import run as rust_run


class BaseDataType(object):
    def example_value(self, default_example_value):
        return self.shape_value(default_example_value) or None

    def return_value_description(self):
        return None

    def shape_value(self, value):
        return value


class List(BaseDataType):
    def example_value(self, default_example_value):
        return default_example_value or [0, 1, 2]

    def return_value_description(self):
        return "List of values (e.g. `[0, 1, 2]`)"

    # def shape_value(self, value):
    #     if value is not None:
    #         return round(value * 1000) / 1000
    #     else:
    #         return 0.0


class Dictionary(BaseDataType):
    def example_value(self, default_example_value):
        return default_example_value or {"key": 0, "key2": 1, "key3": 2}

    def return_value_description(self):
        return 'Dictionary of values (e.g. `{"key": 0, "key2": 1, "key3": 2}`)'

    # def shape_value(self, value):
    #     if value is not None:
    #         return round(value * 1000) / 1000
    #     else:
    #         return 0.0


class Float(BaseDataType):
    def example_value(self, default_example_value):
        return self.shape_value(default_example_value) or 0.1

    def return_value_description(self):
        return "Floating point number (e.g. `0.1`)"

    def shape_value(self, value):
        if value is not None:
            return round(value * 1000) / 1000
        else:
            return 0.0


class Percentage(Float):
    def example_value(self, default_example_value):
        return self.shape_value(default_example_value) or 0.5

    def return_value_description(self):
        return "Percentage as floating point number 0—1 (e.g. `0.5`)"


class Angle(Float):
    def example_value(self, default_example_value):
        return self.shape_value(default_example_value) or -12.5

    def return_value_description(self):
        return "Angle as floating point number (e.g. `-12.5`)"


class Boolean(BaseDataType):
    def example_value(self, default_example_value):
        return self.shape_value(default_example_value) or True

    def return_value_description(self):
        return "Boolean (`True`or `False`)"


class String(BaseDataType):
    def example_value(self, default_example_value):
        return self.shape_value(default_example_value) or "abc..."

    def return_value_description(self):
        return "String"


class Integer(BaseDataType):
    def example_value(self, default_example_value):
        return self.shape_value(default_example_value) or 5

    def return_value_description(self):
        return "Integer number (e.g. `5`)"


class PerMille(Float):
    def example_value(self, default_example_value):
        return self.shape_value(default_example_value) or 1000

    def return_value_description(self):
        return "Per-Mille of UPM (e.g. `1000`)"


class Metric(object):
    name = None
    keyword = None
    children = []
    interpretation_hint = None
    data_type = None
    example_value = None
    fully_automatic = True
    variable_aware = False

    def __init__(self, parent=None) -> None:
        self.parent = parent

        # if variable == "stat":
        #     variable = list(stat_table_combinations(ttFont))
        # elif variable == "fvar":
        #     variable = fvar_instances(ttFont)
        # elif variable == "all":
        #     variable = combined_axis_locations(ttFont)
        # elif type(variable) is str:
        #     variable = instances_str_to_list(variable)
        self.variable = None

    def shape_value(self, value):
        return self.data_type().shape_value(value)

    def paths_for_glyph(self, char, instance=None):
        buf = self.vhb.shape(char, {"variations": instance or {}})
        return self.vhb.buf_to_bezierpaths(buf, penclass=BezPathCreatingPen)

    def find_check(self, path):
        for child in self.children:
            instance = child(self.ttFont, self.vhb, self.variable, parent=self)
            if instance.path() == path.split("/"):
                return instance
            else:
                found = instance.find_check(path)
                if found:
                    return found
        return None

    def is_included(self, includes):
        path = "/".join(self.path())
        # We are at root
        if path == "":
            return True
        if includes:
            for include in includes:
                include_root = include.split("/")[0]
                path_root = path.split("/")[0]
                # We are category root
                if include_root == path_root == path:
                    return True
                # We are normal metric
                elif path.startswith(include):
                    return True
            return False
        else:
            return True

    def is_excluded(self, excludes):
        path = "/".join(self.path())
        # We are at root
        if path == "":
            return False
        if excludes:
            for exclude in excludes:
                exclude_root = exclude.split("/")[0]
                path_root = path.split("/")[0]
                # We are category root
                if exclude_root == path_root == path:
                    return True
                # We are normal metric
                elif path.startswith(exclude):
                    return True
            return False
        else:
            return False

    def value(self, includes=None, excludes=None):

        dictionary = {}
        for child in self.children:
            instance = child(self.ttFont, self.vhb, self.variable, parent=self)
            if instance.is_included(includes) and not instance.is_excluded(excludes):
                dictionary[instance.keyword] = instance.value(includes, excludes)
            elif not includes and not excludes:
                dictionary[instance.keyword] = instance.value(includes, excludes)

        return dictionary

    def path(self):
        if self.parent:
            return self.parent.path() + [self.keyword]
        else:
            return [self.keyword] if self.keyword else []

    def base(self):
        if self.parent:
            return self.parent.base()
        else:
            return self

    def link_list(self):
        if self.__doc__:
            link = "/".join(self.path()).replace("/", "").replace(" ", "-")
            return [
                (
                    f'  * [{self.name}{" 🎛️" if self.variable_aware else ""}]'
                    f'(#{self.name.lower().replace(" ", "-")}-{link})'
                )
            ]
        else:
            check_list = []
            if self.name:
                check_list.append("* " + self.name + ":")
            for child in self.children:
                instance = child(self.ttFont, self.vhb, self.variable, parent=self)
                new_list = instance.link_list()
                if new_list:
                    check_list += new_list
            return check_list

    def index(self):
        if self.__doc__:
            return "/".join(self.path()), self.name
        else:
            check_list = []
            for child in self.children:
                instance = child(self.ttFont, self.vhb, parent=self)
                new_list = instance.index()
                if new_list:
                    check_list += new_list
            return check_list

    def documentation(self):
        join_sequence = '"]["'

        if self.__doc__:
            markdown = f"""\
### {self.name} (`{"/".join(self.path())}`)

{"🎛️ _This metric is variable-aware_" if self.variable_aware else ""}

{" ".join([line.strip() for line in self.__doc__.splitlines()])}
"""
            if self.interpretation_hint:
                markdown += "\n_Interpretation Hint:_ " + (
                    " ".join([line.strip() for line in self.interpretation_hint.splitlines()]) + "\n\n"
                )

            if self.data_type:
                markdown += f"""\n_Return Value:_ {self.data_type().return_value_description()}

"""

            if self.variable_aware:
                var = self.data_type().example_value(self.example_value)
                markdown += f"""_Example with **variable locations**:_
```python
from fontquant import quantify
results = quantify("path/to/font.ttf", locations="wght=400,wdth=100;wght=500,wdth=100")
value = results["{join_sequence.join(self.path())}"]["value"]
print(value)
>>> {{"wdth=100.0,wght=400.0": {var}, "wdth=100.0,wght=500.0": {var}}}
```

**Note:** The axes per instance used in the _return value keys_ will be **sorted alphabetically**
and the _return values_ will be **float** _regardless of your input_.
To identify them in your results, you should also sort and format your input instances accordingly.
You may use `fontquant.helpers.var.sort_instance()` (per instance) or `.sort_instances()` (whole list at once)
for this purpose.

"""
            if self.variable_aware:
                markdown += """_Example with **origin location**:_"""
            else:
                markdown += """_Example:_"""
            markdown += f"""
```python
from fontquant import quantify
results = quantify("path/to/font.ttf")
value = results["{join_sequence.join(self.path())}"]["value"]
print(value)
>>> {self.data_type().example_value(self.example_value)}
```

"""

            return markdown

        else:
            markdown = ""

            if self.name:
                markdown += f"## {self.name}\n\n"

            for child in self.children:
                instance = child(self.ttFont, self.vhb, self.variable, parent=self)
                markdown += instance.documentation()
            return markdown


class Base(Metric):
    children = []


def order_dict(dictionary):
    return {k: order_dict(v) if isinstance(v, dict) else v for k, v in sorted(dictionary.items())}


def quantify(font_path, includes=None, excludes=None, locations=None, debug=False, show=False, primary_script=None):
    base = Base(locations)
    base.debug = debug
    base.show = show
    base.primary_script = primary_script
    value = base.value(includes, excludes)
    # Fill in from Rust
    rust_values = {k: {"value": v} for k, v in rust_run(font_path).items()}
    # Split a/b/c to multilevel hash and merge
    for path, data in rust_values.items():
        keys = path.split("/")
        current_level = value
        for key in keys[:-1]:
            if key not in current_level:
                current_level[key] = {}
            current_level = current_level[key]
        current_level[keys[-1]] = data

    return order_dict(value)
