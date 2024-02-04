# Sphinx-generated HTML documentation is not suitable for packaging; see
# https://bugzilla.redhat.com/show_bug.cgi?id=2006555 for discussion.
#
# We can generate PDF documentation as a substitute.
%bcond doc_pdf 0

%bcond redhat_fonts 0
%bcond adobe_fonts 0

Name:           gi-docgen
Version:        2023.3
Release:        3%{?dist}
Summary:        Documentation tool for GObject-based libraries

# Based on the “Copyright and Licensing terms” in README.md, on the contents of
# .reuse/dep5, and on inspection of SPDX headers or other file contents with
# assistance from licensecheck.
#
# The entire source is (Apache-2.0 OR GPL-3.0-or-later) except the following files that are
# packaged or are used to generate packaged files:
#
# (Apache-2.0 OR GPL-3.0-or-later) AND BSD-2-Clause:
#   - gidocgen/mdext.py
#
# MIT:
#   - gidocgen/templates/basic/fzy.js
#   - gidocgen/templates/basic/solarized-{dark,light}.js
#
# CC0-1.0:
#   - gi-docgen.pc.in (from which gi-docgen.pc is generated)
#   - gidocgen/templates/basic/*.png
#   - docs/CODEOWNERS (-doc subpackage)
#   - examples/*.toml (-doc subpackage)
#
# Note that CC0-1.0 is allowed in Fedora for content only; all of the above
# files may reasonably be called content.
#
# Additionally, CC0-1.0 appears in certain sample configuration snippets within
# the following files, which are otherwise (Apache-2.0 OR GPL-3.0-or-later):
#   - docs/project-configuration.rst
#   - docs/tutorial.rst
# On one hand, these are copied from real projects; on the other hand, they are
# very trivial. It’s not obvious whether they should be considered “real”
# CC0-1.0 content or not.
#
# The identifier LGPL-2.1-or-later also appears in a sample configuration
# template in docs/tutorial.rst, but the configuration in question is filled
# with placeholder values and is not copied from a real project, so it’s
# reasonable to consider LGPL-2.1-or-later a placeholder rather than a real
# license as well.
#
# -----
#
# Additionally, the following sources are under licenses other than (Apache-2.0
# OR GPL-3.0-or-later), but are not packaged in any of the binary RPMs:
#
# CC0-1.0:
#   - .editorconfig (not installed)
#   - .gitlab-ci.yml (not installed)
#   - gi-docgen.doap (not installed)
#   - MANIFEST.in (not installed)
#   - pytest.ini (not installed; test only)
#   - tests/data/config/*.toml (not installed; test only)
#
# CC-BY-SA-3.0:
#   - docs/gi-docgen.{png,svg} (for HTML docs; not currently packaged)
#   - code-of-conduct.md (not installed)
#
# OFL-1.1:
#   - gidocgen/templates/basic/*.{woff,woff2} (removed in prep)
#
# GPL-2.0-or-later:
#   - tests/data/gir/{Utility-1.0,Regress-1.0}.gir (not installed; test only)
#
# LGPL-2.0-or-later:
#   - tests/data/gir/{GLib,GObject,Gio}-2.0.gir (not installed; test only)
#
# LGPL-2.0-or-later OR MPL-1.1:
#   - tests/data/gir/cairo-1.0.gir (not installed; test only)
License:        %{shrink:
                (Apache-2.0 OR GPL-3.0-or-later) AND
                BSD-2-Clause AND
                MIT AND
                CC0-1.0
                }
URL:            https://gitlab.gnome.org/GNOME/gi-docgen
Source:         %{url}/-/archive/%{version}/gi-docgen-%{version}.tar.bz2

# We are prohibited from bundling fonts, and we are prohibited from shipping
# fonts in web font formats; see
# https://docs.fedoraproject.org/en-US/packaging-guidelines/FontsPolicy/#_web_fonts.
#
# Since upstream uses *only* web fonts, we need a patch. We haven’t offered it
# upstream since upstream has no reason NOT to use web fonts.
#
# This patch removes all references to WOFF/WOFF2 font files (which we still
# must remove in %%prep) and ensures the CSS correctly references corresponding
# local system fonts.
Patch:          gi-docgen-2022.2-no-web-fonts.patch

# https://gitlab.gnome.org/GNOME/gi-docgen/-/issues/179
Patch:          fix-broken-since-obsoletes.patch

BuildArch:      noarch

BuildRequires:  python3-devel

BuildRequires:  python3dist(pytest)

# Documentation
%if %{with doc_pdf}
BuildRequires:  make
BuildRequires:  python3dist(sphinx)
BuildRequires:  python3dist(sphinx-rtd-theme)
BuildRequires:  python3-sphinx-latex
BuildRequires:  latexmk
%endif

# Unbundling fonts:
%if %{with redhat_fonts}
BuildRequires:  font(redhatdisplay)
BuildRequires:  font(redhatdisplayblack)
BuildRequires:  font(redhatdisplaymedium)
BuildRequires:  font(redhattext)
BuildRequires:  font(redhattextmedium)
%endif
%if %{with adobe_fonts}
BuildRequires:  font(sourcecodepro)
BuildRequires:  font(sourcecodeprosemibold)
%endif

# Azure Linux provides freefont
BuildRequires:       freefont

# Unbundling fonts:
Requires:       gi-docgen-fonts = %{version}-%{release}

# Trivial fork of https://github.com/jhawthorn/fzy.js (looks like it was
# basically just wrapped in an IIFE). Given that modification, it’s not clear
# how we could unbundle it, either downstream or with some kind of upstream
# support.
#
# It’s not clear what version was used for the fork.
Provides:       bundled(js-fzy)

%description
GI-DocGen is a document generator for GObject-based libraries. GObject is the
base type system of the GNOME project. GI-Docgen reuses the introspection data
generated by GObject-based libraries to generate the API reference of these
libraries, as well as other ancillary documentation.

GI-DocGen is not a general purpose documentation tool for C libraries.

While GI-DocGen can be used to generate API references for most GObject/C
libraries that expose introspection data, its main goal is to generate the
reference for GTK and its immediate dependencies. Any and all attempts at
making this tool more generic, or to cover more use cases, will be weighted
heavily against its primary goal.

GI-DocGen is still in development. The recommended use of GI-DocGen is to add
it as a sub-project to your Meson build system, and vendor it when releasing
dist archives.

You should not depend on a system-wide installation until GI-DocGen is declared
stable.


%package fonts
Summary:        Metapackage providing fonts for gi-docgen output
# Really, there is nothing copyrightable in this metapackage, so we give it the
# overall license of the project.
License:        Apache-2.0 OR GPL-3.0-or-later

%if %{with redhat_fonts}
Requires:       font(redhatdisplay)
Requires:       font(redhatdisplayblack)
Requires:       font(redhatdisplaymedium)
Requires:       font(redhattext)
Requires:       font(redhattextmedium)
%endif
%if %{with adobe_fonts}
Requires:       font(sourcecodepro)
Requires:       font(sourcecodeprosemibold)
%endif

# Azure Linux provides freefont
Requires:       freefont

%description fonts
Because web fonts from upstream are not bundled in the gi-docgen package,
documentation packages generated with gi-docgen must depend on this metapackage
to ensure the proper system fonts are present.


%package doc
Summary:        Documentation for gi-docgen
License:        (Apache-2.0 OR GPL-3.0-or-later) AND CC0-1.0

%description doc
Documentation for gi-docgen.


%generate_buildrequires
%pyproject_buildrequires


%prep
%autosetup -p1

# Remove all bundled fonts. See gi-docgen-*-no-web-fonts.patch.
find . -type f \( -name '*.woff' -o -name '*.woff2' \) -print -delete


%build
%pyproject_wheel

%if %{with doc_pdf}
sphinx-build -b latex -j%{?_smp_build_ncpus} docs %{_vpath_builddir}/_latex
%make_build -C %{_vpath_builddir}/_latex LATEXMKOPTS='-quiet'
%endif


%install
%pyproject_install
%pyproject_save_files gidocgen

install -t '%{buildroot}%{_pkgdocdir}' -D -m 0644 -p \
    CHANGES.md \
    CONTRIBUTING.md \
    docs/CODEOWNERS \
    README.md
%if %{with doc_pdf}
install -t '%{buildroot}%{_pkgdocdir}' -p -m 0644 \
    '%{_vpath_builddir}/_latex/gi-docgen.pdf'
%endif
cp -rp examples '%{buildroot}%{_pkgdocdir}/'


%check
%pytest


%files -f %{pyproject_files}
%license LICENSES/ .reuse/dep5

%{_bindir}/gi-docgen
%{_mandir}/man1/gi-docgen.1*
# Normally, this would go in a -devel package, but there is little point in
# providing a -devel package for *just* the .pc file when there are no
# libraries or headers.
%{_datadir}/pkgconfig/gi-docgen.pc


%files fonts
# Empty; this is a metapackage


%files doc
%license LICENSES/ .reuse/dep5
%doc %{_pkgdocdir}/


%changelog
* Sat Feb  3 16:37:44 EST 2024 Dan Streetman <ddstreet@ieee.org> - 2023.3-3
- Update to version from Fedora 39.
- Next line is present only to avoid tooling failures, and does not indicate the actual package license.
- Initial CBL-Mariner import from Fedora 39 (license: MIT).
- license verified

* Mon 18 Dec 2023 12:00:00 AM  Michael Catanzaro <mcatanzaro@redhat.com> - 2023.3-2
- Add patch to fix broken Since/Obsoletes

* Sun 26 Nov 2023 12:00:00 AM  Benjamin A. Beasley <code@musicinmybrain.net> - 2023.3-1
- Update to 2023.3 (close RHBZ#2251397)

* Sun 26 Nov 2023 12:00:00 AM  Benjamin A. Beasley <code@musicinmybrain.net> - 2023.1-10
- Package LICENSES/ as a directory

* Wed 19 Jul 2023 12:00:00 AM  Fedora Release Engineering <releng@fedoraproject.org> - 2023.1-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Fri 07 Jul 2023 12:00:00 AM  Benjamin A. Beasley <code@musicinmybrain.net> - 2023.1-8
- Use new (rpm 4.17.1+) bcond style

* Thu 15 Jun 2023 12:00:00 AM  Python Maint <python-maint@redhat.com> - 2023.1-7
- Rebuilt for Python 3.12

* Fri 17 Mar 2023 12:00:00 AM  Benjamin A. Beasley <code@musicinmybrain.net> - 2023.1-3
- Don’t assume %_smp_mflags is -j%_smp_build_ncpus

* Thu 19 Jan 2023 12:00:00 AM  Fedora Release Engineering <releng@fedoraproject.org> - 2023.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Sat 07 Jan 2023 12:00:00 AM  Benjamin A. Beasley <code@musicinmybrain.net> - 2023.1-1
- Update to 2023.1 (close RHBZ#2158850)

* Fri 30 Dec 2022 12:00:00 AM  Miro Hrončok <miro@hroncok.cz> - 2022.2-3
- Use tomllib (tomli) instated of deprecated python3-toml

* Mon 18 Dec 2023 12:00:00 AM  Michael Catanzaro <mcatanzaro@redhat.com> - 2023.3-2
- Add patch to fix broken Since/Obsoletes

* Sun 26 Nov 2023 12:00:00 AM  Benjamin A. Beasley <code@musicinmybrain.net> - 2023.3-1
- Update to 2023.3 (close RHBZ#2251397)

* Sun 26 Nov 2023 12:00:00 AM  Benjamin A. Beasley <code@musicinmybrain.net> - 2023.1-10
- Package LICENSES/ as a directory

* Wed 19 Jul 2023 12:00:00 AM  Fedora Release Engineering <releng@fedoraproject.org> - 2023.1-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Fri 07 Jul 2023 12:00:00 AM  Benjamin A. Beasley <code@musicinmybrain.net> - 2023.1-8
- Use new (rpm 4.17.1+) bcond style

* Thu 15 Jun 2023 12:00:00 AM  Python Maint <python-maint@redhat.com> - 2023.1-7
- Rebuilt for Python 3.12

* Fri 17 Mar 2023 12:00:00 AM  Benjamin A. Beasley <code@musicinmybrain.net> - 2023.1-3
- Don’t assume %_smp_mflags is -j%_smp_build_ncpus

* Thu 19 Jan 2023 12:00:00 AM  Fedora Release Engineering <releng@fedoraproject.org> - 2023.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Sat 07 Jan 2023 12:00:00 AM  Benjamin A. Beasley <code@musicinmybrain.net> - 2023.1-1
- Update to 2023.1 (close RHBZ#2158850)

* Fri 30 Dec 2022 12:00:00 AM  Miro Hrončok <miro@hroncok.cz> - 2022.2-3
- Use tomllib (tomli) instated of deprecated python3-toml

* Fri Jun 25 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 2021.6-1
- Initial package
