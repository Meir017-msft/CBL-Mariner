%bcond as_wget 1
%global somajor 2

Name:           wget2
Version:        2.1.0
Release:        8%{?dist}
Summary:        An advanced file and recursive website downloader

# Documentation is GFDL
License:        GPL-3.0-or-later AND LGPL-3.0-or-later AND GFDL-1.3-or-later
URL:            https://gitlab.com/gnuwget/wget2
Source0:        https://ftp.gnu.org/gnu/wget/%{name}-%{version}.tar.gz

# Backports from upstream
## Fix behavior for downloading to stdin (rhbz#2257700, gl#gnuwget/wget2#651)
Patch0001:      0001-src-log.c-log_init-Redirect-INFO-logs-to-stderr-with.patch

# Buildsystem build requirements
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  flex-devel >= 2.5.35
BuildRequires:  gettext >= 0.18.2
BuildRequires:  gcc
BuildRequires:  make

# Documentation build requirements
BuildRequires:  doxygen
BuildRequires:  git-core

# Wget2 build requirements
BuildRequires:  bzip2-devel
BuildRequires:  python3
BuildRequires:  tar
BuildRequires:  texinfo
BuildRequires:  pkgconfig(gnutls)
BuildRequires:  pkgconfig(gpgme)
BuildRequires:  pkgconfig(libbrotlidec)
## Not available yet
#BuildRequires:  pkgconfig(liblz)
BuildRequires:  pkgconfig(liblzma)
BuildRequires:  pkgconfig(libnghttp2)
BuildRequires:  pkgconfig(libpcre2-8)
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(zlib)

Provides:       webclient
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description
GNU Wget2 is the successor of GNU Wget, a file and recursive website
downloader.

Designed and written from scratch it wraps around libwget, that provides the
basic functions needed by a web client.

Wget2 works multi-threaded and uses many features to allow fast operation.
In many cases Wget2 downloads much faster than Wget1.x due to HTTP2, HTTP
compression, parallel connections and use of If-Modified-Since HTTP header.

%package libs
Summary:        Runtime libraries for GNU Wget2
# There's some gnulib in there :)
Provides:       bundled(gnulib)

%description libs
This package contains the libraries for applications to use
Wget2 functionality.

%package devel
Summary:        Libraries and header files needed for using wget2 libraries
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description devel
Development libraries and headers needed for building applications to
use functionality from GNU Wget2.

%if %{with as_wget}
%package wget
Summary:        %{name} shim to provide wget
Requires:       wget2%{?_isa} = %{version}-%{release}
# Replace wget
Conflicts:      wget < 2
Obsoletes:      wget < 2
Provides:       wget = %{version}-%{release}
Provides:       wget%{?_isa} = %{version}-%{release}
# From original wget package
Provides:       webclient

%description wget
This package provides the shim links for %{name} to be automatically
used in place of wget. This ensures that %{name} is used as
the system provider of wget.
%endif

%prep
%autosetup -p1


%build
%configure --disable-static
# Remove RPATH, rely on default -Wl,--enable-new-dtags in Fedora.
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
%make_build


%install
%make_install
%find_lang %{name}

# tarball includes a pre-built manpage
install -D -m0644 -t %{buildroot}%{_mandir}/man1/ docs/man/man1/wget2.1

# Purge all libtool archives
find %{buildroot} -type f -name "*.la" -delete -print

# Delete useless noinstall binary
rm -v %{buildroot}%{_bindir}/%{name}_noinstall

%if %{with as_wget}
ln -sr %{buildroot}%{_bindir}/%{name} %{buildroot}%{_bindir}/wget
# Link wget(1) to wget2(1)
echo ".so man1/%{name}.1" > %{buildroot}%{_mandir}/man1/wget.1
%endif

%check
%make_build check


%files -f %{name}.lang
%license COPYING*
%doc README.md
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*

%files libs
%license COPYING*
%{_libdir}/libwget*.so.%{somajor}{,.*}

%files devel
%{_includedir}/wget.h
%{_includedir}/wgetver.h
%{_libdir}/libwget*.so
%{_libdir}/pkgconfig/libwget.pc
%{_mandir}/man3/libwget*.3*

%if %{with as_wget}
%files wget
%{_bindir}/wget
%{_mandir}/man1/wget.1*
%endif


%changelog
* Mon Feb 05 2024 Muhammad Falak <mwanin@microsoft.com> - 2.1.0-8
- Switch wget from 1.x to 2.x
- Initial CBL-Mariner import from Fedora 40 (license: MIT).
- License Verified

* Sat Jan 27 2024 Fedora Release Engineering <releng@fedoraproject.org> - 2.1.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Sun Jan 14 2024 Neal Gompa <ngompa@fedoraproject.org> - 2.1.0-6
- Backport fix for wget to stdin
  Resolves: rhbz#2257700

* Thu Jan 04 2024 Yaakov Selkowitz <yselkowi@redhat.com> - 2.1.0-5
- Drop unused autogen build dependency

* Thu Dec 21 2023 Yaakov Selkowitz <yselkowi@redhat.com> - 2.1.0-4
- Avoid pandoc dependency on RHEL
- Fix tests on RHEL

* Sat Dec 16 2023 Neal Gompa <ngompa@fedoraproject.org> - 2.1.0-3
- Enable wget2-wget for F40+ / RHEL10+

* Fri Sep 01 2023 Mikel Olasagasti Uranga <mikel@olasagasti.info> - 2.1.0-2
- Add gpg signature check

* Fri Sep 01 2023 Neal Gompa <ngompa@fedoraproject.org> - 2.1.0-1
- New upstream version
- Add conditional for using wget2 as wget

* Sat Jul 22 2023 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Tue Mar 21 2023 Michal Ruprich <mruprich@redhat.com> - 2.0.0-5
- SPDX migration

* Sat Jan 21 2023 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Sat Jul 23 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Sat Jan 22 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Sun Sep 26 2021 Neal Gompa <ngompa@fedoraproject.org> - 2.0.0-1
- Rebase to 2.0.0 final
- Split out libraries into libs subpackage
- Delete unwanted static subpackage

* Wed Apr  1 2020 Anna Khaitovich <akhaitov@redhat.com> - 1.99.2-1
- Initial package



