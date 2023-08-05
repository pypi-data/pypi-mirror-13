# -*- coding: utf-8 -*-

import os
import cgi
import re
import tempfile
import shutil

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.ext.code import CodeExtension
from wheezy.template.loader import FileLoader

from ...core.symbols import *
from ...core.base_formatter import Formatter
from ...core.links import Link

class TocSection (object):
    def __init__(self, summaries, name):
        self.summaries = summaries
        self.name = name
        self.id_ = ''.join(name.split())

class SymbolDescriptions (object):
    def __init__(self, descriptions, name):
        self.descriptions = descriptions
        self.name = name

class HtmlFormatter (Formatter):
    def __init__(self, doc_tool, searchpath):
        Formatter.__init__(self, doc_tool)

        self._symbol_formatters = {
                FunctionSymbol: self._format_function,
                FunctionMacroSymbol: self._format_function_macro,
                CallbackSymbol: self._format_callback,
                ConstantSymbol: self._format_constant,
                ExportedVariableSymbol: self._format_constant,
                AliasSymbol: self._format_alias,
                StructSymbol: self._format_struct,
                EnumSymbol: self._format_enum,
                ParameterSymbol: self._format_parameter_symbol,
                ReturnValueSymbol : self._format_return_value_symbol,
                FieldSymbol: self._format_field_symbol,
                SignalSymbol: self._format_signal_symbol,
                VFunctionSymbol: self._format_vfunction_symbol,
                PropertySymbol: self._format_property_symbol,
                ClassSymbol: self._format_class_symbol,
                }

        self._summary_formatters = {
                FunctionSymbol: self._format_function_summary,
                FunctionMacroSymbol: self._format_function_macro_summary,
                CallbackSymbol: self._format_callback_summary,
                ConstantSymbol: self._format_constant_summary,
                ExportedVariableSymbol: self._format_exported_variable_summary,
                AliasSymbol: self._format_alias_summary,
                StructSymbol: self._format_struct_summary,
                EnumSymbol: self._format_enum_summary,
                SignalSymbol: self._format_signal_summary,
                VFunctionSymbol: self._format_vfunction_summary,
                PropertySymbol: self._format_property_summary,
                ClassSymbol: self._format_class_summary,
                }

        self._ordering = [ClassSymbol, FunctionSymbol, FunctionMacroSymbol, SignalSymbol,
                PropertySymbol, StructSymbol, VFunctionSymbol, EnumSymbol, ConstantSymbol,
                ExportedVariableSymbol, AliasSymbol, CallbackSymbol]

        module_path = os.path.dirname(__file__)

        self.__theme_path = doc_tool.html_theme_path
        self.__parse_theme(searchpath)

        searchpath.append (os.path.join(module_path, "templates"))
        self.engine = Engine(
            loader=FileLoader(searchpath, encoding='UTF-8'),
            extensions=[CoreExtension(), CodeExtension()]
        )

        self.editing_server = doc_tool.editing_server

        self.all_scripts = set()

    def __parse_theme(self, searchpath):
        if not self.__theme_path:
            return
        searchpath.insert (0, os.path.join(self.__theme_path, 'templates'))

    def _get_extension (self):
        return "html"

    def _format_link (self, link, title):
        out = ''
        if not link:
            print "Issue here plz check", title
            return title

        template = self.engine.get_template('link.html')
        out += '%s' % template.render ({'link': link,
                                         'link_title': title})
        return out

    def _format_type_tokens (self, type_tokens):
        out = ''
        link_before = False

        for tok in type_tokens:
            if isinstance (tok, Link):
                ref = tok.get_link()
                if ref:
                    out += self._format_link (ref, tok.title)
                    link_before = True
                else:
                    if link_before:
                        out += ' '
                    out += tok.title
                    link_before = False
            else:
                if link_before:
                    out += ' '
                out += tok
                link_before = False

        return out

    def _format_linked_symbol (self, symbol):
        out = ""

        if isinstance (symbol, QualifiedSymbol):
            out += self._format_type_tokens (symbol.type_tokens)

        # FIXME : ugly
        elif hasattr (symbol, "link"):
            out += self._format_link (symbol.link.get_link(), symbol.link.title)

        if type (symbol) == ParameterSymbol:
            out += ' ' + symbol.argname

        if type (symbol) == FieldSymbol and symbol.member_name:
            template = self.engine.get_template('inline_code.html')
            member_name = template.render ({'code': symbol.member_name})
            if symbol.is_function_pointer:
                out = member_name
                out += "()"
            else:
                out += ' ' + member_name

        return out

    def _format_callable_prototype (self, return_value, function_name,
            parameters, is_pointer):
        template = self.engine.get_template('callable_prototype.html')

        return template.render ({'return_value': return_value,
                                 'name': function_name,
                                 'parameters': parameters,
                                 'is_pointer': is_pointer,
                                })

    def __format_parameter_detail (self, name, detail, extra={}):
        template = self.engine.get_template('parameter_detail.html')
        return template.render ({'name': name,
                                 'detail': detail,
                                 'extra': extra
                                })

    def _format_callable_summary (self, callable_, return_value, function_name,
            is_callable, is_pointer):
        template = self.engine.get_template('callable_summary.html')

        return template.render({'symbol': callable_,
                                'return_value': return_value,
                                'function_name': function_name,
                                'is_callable': is_callable,
                                'is_pointer': is_pointer,
                               })

    def _format_function_summary (self, func):
        return self._format_callable_summary (
                func,
                self._format_linked_symbol (func.return_value),
                self._format_linked_symbol (func),
                True,
                False)

    def _format_callback_summary (self, callback):
        return self._format_callable_summary (
                callback,
                self._format_linked_symbol (callback.return_value),
                self._format_linked_symbol (callback),
                True,
                True)

    # FIXME : C-specific
    def _format_function_macro_summary (self, func):
        return self._format_callable_summary (
                func,
                "#define ",
                self._format_linked_symbol (func),
                True,
                False)

    def _format_constant_summary (self, constant):
        template = self.engine.get_template('constant_summary.html')
        constant_link = self._format_linked_symbol (constant)

        return template.render({'symbol': constant,
                                'constant': constant_link})

    def _format_exported_variable_summary (self, extern):
        template = self.engine.get_template('exported_variable_summary.html')
        type_link = self._format_linked_symbol(extern.type_qs)
        extern_link = self._format_linked_symbol (extern)

        return template.render({'symbol': extern,
                                'type_link': type_link,
                                'extern': extern_link})

    def _format_alias_summary (self, alias):
        template = self.engine.get_template('alias_summary.html')
        alias_link = self._format_linked_symbol (alias)

        return template.render({'symbol': alias,
                                'alias': alias_link})

    def _format_struct_summary (self, struct):
        template = self.engine.get_template('struct_summary.html')
        struct_link = self._format_linked_symbol (struct)
        return template.render({'symbol': struct,
                                'struct': struct_link})

    def _format_enum_summary (self, enum):
        template = self.engine.get_template('enum_summary.html')
        enum_link = self._format_linked_symbol (enum)
        return template.render({'symbol': enum,
                                'enum': enum_link})

    def _format_signal_summary (self, signal):
        return self._format_callable_summary (
                signal,
                self._format_linked_symbol (signal.return_value),
                self._format_linked_symbol (signal),
                True,
                False)

    def _format_vfunction_summary (self, vmethod):
        return self._format_callable_summary (
                vmethod,
                self._format_linked_symbol (vmethod.return_value),
                self._format_linked_symbol (vmethod),
                True,
                True)

    def _format_property_summary (self, prop):
        template = self.engine.get_template('property_summary.html')
        property_type = self._format_linked_symbol (prop.prop_type)

        prop_link = self._format_linked_symbol (prop)

        return template.render({'symbol': prop,
                                'property_type': property_type,
                                'property_link': prop_link,
                                'extra_contents': prop.extension_contents,
                               })

    def _format_class_summary (self, klass):
        if not klass.comment:
            return ''

        short_desc = self._format_doc_string (klass.comment.short_description)
        template = self.engine.get_template('class_summary.html')
        return template.render({'symbol': klass,
                                'klass': klass,
                                'short_description': short_desc})

    def _format_summary (self, toc_sections):
        template = self.engine.get_template('summary.html')

        return template.render({'toc_sections': toc_sections,
                               })

    def _format_symbols_toc_section (self, symbols_type, symbols_list):
        summary_formatter = self._summary_formatters.get(symbols_type)

        toc_section_summaries = []
        detailed_descriptions = []
        
        for element in symbols_list.symbols:
            if element.skip:
                continue
            if summary_formatter:
                summary = summary_formatter(element)
                if summary:
                    toc_section_summaries.append (summary)
            if element.detailed_description:
                detailed_descriptions.append (element.detailed_description)

        symbol_type = symbols_list.name

        toc_section = None
        if toc_section_summaries:
            toc_section = TocSection (toc_section_summaries, symbol_type)

        symbol_descriptions = None
        if detailed_descriptions:
            symbol_descriptions = SymbolDescriptions (detailed_descriptions,
                    symbol_type)

        return (toc_section, symbol_descriptions)

    def _format_editing_link(self, symbol):
        if not self.editing_server:
            return None

        template = self.engine.get_template("editing_link.html")
        return template.render({"symbol": symbol,
                                "editing_server": self.editing_server})

    def _format_struct (self, struct):
        raw_code = None
        if struct.raw_text is not None:
            raw_code = self._format_raw_code (struct.raw_text)

        members_list = self._format_members_list (struct.members, 'Fields')

        template = self.engine.get_template ("struct.html")
        out = template.render ({"symbol": struct,
                                "editing_link": self._format_editing_link(struct),
                                "struct": struct,
                                "raw_code": raw_code,
                                "members_list": members_list})
        return (out, False)

    def _format_enum (self, enum):
        for member in enum.members:
            template = self.engine.get_template ("enum_member.html")
            member.detailed_description = template.render ({
                                    'link': member.link,
                                    'detail': member.formatted_doc,
                                    'value': str (member.enum_value)})

        members_list = self._format_members_list (enum.members, 'Members')
        template = self.engine.get_template ("enum.html")
        out = template.render ({"symbol": enum,
                                "editing_link": self._format_editing_link(enum),
                                "enum": enum,
                                "members_list": members_list})
        return (out, False)

    def emit_formatting_page(self, page):
        page.output_attrs['html']['scripts'] = set()
        return Formatter.emit_formatting_page(self, page)

    def _format_page(self, page):
        page.formatted_contents = self.doc_tool.doc_tree.page_parser.render(page)

        toc_sections = []
        symbols_details = []

        for symbols_type in self._ordering:
            symbols_list = page.typed_symbols.get(symbols_type)
            if not symbols_list:
                continue

            toc_section, symbols_descriptions = \
                    self._format_symbols_toc_section (symbols_type,
                            symbols_list)

            if toc_section:
                toc_sections.append(toc_section)
            if symbols_descriptions:
                symbols_details.append (symbols_descriptions) 

        template = self.engine.get_template('page.html')

        toc = self._format_summary(toc_sections)

        scripts = page.output_attrs['html']['scripts']
        scripts_basenames = [os.path.basename(script)
                for script in scripts]

        self.all_scripts.update(scripts)

        out = template.render ({'page': page,
                                'site_navigation': self.doc_tool.site_navigation,
                                'scripts': scripts_basenames,
                                'toc': toc,
                                'assets_path': self._get_assets_path(),
                                'symbols_details': symbols_details})

        return (out, True)

    def format_site_navigation(self, root):
        template = self.engine.get_template('site_navigation.html')
        if template:
            return template.render({'root': root,
                                    'doc_tree': self.doc_tool.doc_tree,
                                   })
        return None

    def _format_prototype (self, function, is_pointer, title):
        return_value = self._format_linked_symbol (function.return_value)
        parameters = []
        for param in function.parameters:
            parameters.append (self._format_linked_symbol(param))

        return self._format_callable_prototype (return_value,
                title, parameters, is_pointer)

    def _format_raw_code (self, code):
        code = cgi.escape(code)
        template = self.engine.get_template('raw_code.html')
        return template.render ({'code': code})

    def _format_parameter_symbol (self, parameter):
        return (self.__format_parameter_detail (parameter.argname,
                parameter.formatted_doc, extra=parameter.extension_contents), False)

    def _format_field_symbol (self, field):
        field_id = self._format_linked_symbol (field) 
        return (self.__format_parameter_detail (field_id,
            field.formatted_doc), False)

    def _format_return_value_symbol(self, return_value):
        if not return_value or not return_value.formatted_doc:
            return ('', False)
        template = self.engine.get_template('return_value.html')
        return (template.render ({'return_value': return_value}), False)

    def _format_callable(self, callable_, callable_type, title,
            is_pointer=False):
        template = self.engine.get_template('callable.html')

        parameters = [p.detailed_description for p in callable_.parameters if
                p.detailed_description is not None]

        prototype = self._format_prototype (callable_, is_pointer, title)

        return_value_detail = None
        if callable_.return_value:
            return_value_detail = callable_.return_value.detailed_description

        tags = {}
        if callable_.comment:
            tags = callable_.comment.tags

        tags.pop('returns', None)

        out = template.render ({'prototype': prototype,
                                'symbol': callable_,
                                "editing_link": self._format_editing_link(callable_),
                                'return_value': return_value_detail,
                                'parameters': parameters,
                                'callable_type': callable_type,
                                'tags': tags,
                                'extra': callable_.extension_contents})

        return (out, False)

    def _format_signal_symbol (self, signal):
        title = "%s_callback" % re.sub ('-', '_', signal.link.title)
        return self._format_callable (signal, "signal", title)

    def _format_vfunction_symbol (self, vmethod):
        return self._format_callable (vmethod, "virtual method", vmethod.link.title)

    def _format_property_symbol (self, prop):
        type_link = self._format_linked_symbol (prop.prop_type)
        template = self.engine.get_template ('property_prototype.html')
        prototype = template.render ({'property_name': prop.link.title,
                                      'property_type': type_link})
        template = self.engine.get_template ('property.html')
        res = template.render ({'symbol': prop,
                                "editing_link": self._format_editing_link(prop),
                                'prototype': prototype,
                                'property': prop,
                                'extra': prop.extension_contents})
        return (res, False)

    def _format_class_symbol (self, klass):
        hierarchy = []
        children = []
        for p in klass.hierarchy:
            hierarchy.append(self._format_linked_symbol (p))
        for c in klass.children.itervalues():
            children.append(self._format_linked_symbol (c))

        if hierarchy or children:
            template = self.engine.get_template ("hierarchy.html")
            hierarchy = template.render ({'hierarchy': hierarchy,
                                        'children': children,
                                        'klass': klass})

        template = self.engine.get_template ('class.html')
        return (template.render ({'symbol': klass,
                                  "editing_link": self._format_editing_link(klass),
                                  'klass': klass,
                                  'hierarchy': hierarchy}),
                False)

    def _format_members_list(self, members, member_designation):
        template = self.engine.get_template('member_list.html')
        return template.render ({'members': members,
            'member_designation': member_designation})

    def _format_function(self, function):
        return self._format_callable (function, "method", function.link.title)

    def _format_callback (self, callback):
        return self._format_callable (callback, "callback",
                callback.link.title, is_pointer=True)

    def _format_function_macro(self, function_macro):
        template = self.engine.get_template('callable.html')
        prototype = self._format_raw_code (function_macro.original_text)

        parameters = [p.detailed_description for p in function_macro.parameters
                if p.detailed_description is not None]

        return_value_detail = None
        if function_macro.return_value:
            return_value_detail = function_macro.return_value.detailed_description

        out = template.render ({'prototype': prototype,
                                'symbol': function_macro,
                                "editing_link": self._format_editing_link(function_macro),
                                'return_value': return_value_detail,
                                'parameters': parameters,
                                'callable_type': "function macro",
                                'flags': None,
                                'tags': {},
                                'extra': function_macro.extension_contents})

        return (out, False)

    def _format_alias (self, alias):
        template = self.engine.get_template('alias.html')
        aliased_type = self._format_linked_symbol (alias.aliased_type)
        return (template.render ({'symbol': alias,
                                  "editing_link": self._format_editing_link(alias),
                                  'alias': alias,
                                  'aliased_type': aliased_type}), False)

    def _format_constant(self, constant):
        template = self.engine.get_template('constant.html')
        definition = self._format_raw_code (constant.original_text)
        out = template.render ({'symbol': constant,
                                "editing_link": self._format_editing_link(constant),
                                'definition': definition,
                                'constant': constant})
        return (out, False)

    def _format_symbol (self, symbol):
        format_function = self._symbol_formatters.get(type(symbol))
        if format_function:
            return format_function (symbol)
        return (None, False)

    def _format_object_hierarchy_symbol (self, symbol):
        dot_graph = self._create_hierarchy_graph (symbol.hierarchy)
        f = tempfile.NamedTemporaryFile(suffix='.svg', delete=False)
        dot_graph.draw(f, prog='dot', format='svg', args="-Grankdir=LR")
        f.close()
        with open (f.name, 'r') as f:
            contents = f.read()
        os.unlink(f.name)

        pagename = 'object_hierarchy.html'
        template = self.engine.get_template(pagename)
        res = template.render({'graph': contents,
                                'assets_path': self._get_assets_path(),
                                })
        return (res, False)

    def _get_assets_path(self):
        return 'assets'

    def _get_extra_files (self):
        dir_ = os.path.dirname(__file__)
        res = []

        if self.__theme_path:
            theme_files = os.listdir(self.__theme_path)
            theme_files.remove('templates')
            theme_files = [os.path.join(self.__theme_path, dir_) for dir_ in
                    theme_files]

            res.extend(theme_files)

        return res

    def _copy_extra_files(self):
        Formatter._copy_extra_files(self)

        js_path = os.path.join (self.doc_tool.output, 'assets', 'js')
        if not os.path.exists (js_path):
            os.mkdir (js_path)

        for script in self.all_scripts:
            dest = os.path.join(js_path, os.path.basename(script))
            shutil.copy(script, dest)
