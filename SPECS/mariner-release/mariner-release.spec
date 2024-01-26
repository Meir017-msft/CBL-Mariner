
# Temporary transition from mariner->azure
%{?mariner_release_version:%define azure_release_version %mariner_release_version}

# This MUST be built with %azure_release_version externally defined (e.g. by the build tools).
# This package CANNOT be built using standard tooling (e.g. rpmbuild, mock, etc) without also manually defining the macro.
%{!?azure_release_version:%{error:This package must be built with azure_release_version externally defined.}}

%define get_version_major() %{lua: _, _, v = string.find(arg[1], "(%d+)%.?"); print(v)}
%define get_version_minor() %{lua: _, _, v = string.find(arg[1], "%d+%.(%d+)%.?"); print(v or 0)}
%define get_version_date() %{lua: _, _, v = string.find(arg[1], "%d+%.%d+%.(%d+)"); print(v or 0)}

%global dist_version %azure_release_version
%define dist_version_major %get_version_major %dist_version
%define dist_version_minor %get_version_minor %dist_version
%define dist_version_date  %get_version_date  %dist_version

%global dist_vendor Microsoft Corporation
%global dist_name   Microsoft Azure Linux
%global dist_home_url https://aka.ms/azurelinux

Summary:        Azure Linux release files
Name:           mariner-release
Version:        %{dist_version_major}.%{dist_version_minor}
Release:        2%{?dist}
License:        MIT
Group:          System Environment/Base
Vendor:         %dist_vendor
Distribution:   %dist_name
URL:            %dist_home_url

Source1:        90-default.preset
Source2:        90-default-user.preset
Source3:        99-default-disable.preset

Provides:       azure-release = %{version}-%{release}
Provides:       azure-release-variant = %{version}-%{release}

Provides:       system-release
Provides:       system-release(%{version})
Requires:       azure-release-common = %{version}-%{release}

BuildArch:      noarch

# azure-release-common Requires: azure-release-identity, so at least one
# package must provide it. This Recommends: pulls in
# azure-release-identity-basic if nothing else is already doing so.
Recommends:     azure-release-identity-basic

BuildRequires:  redhat-rpm-config > 121-1
BuildRequires:  systemd-rpm-macros

%description
Azure Linux release files such as dnf configs and other %{_sysconfdir}/ release related files
and systemd preset files that determine which services are enabled by default.


%package common
Summary: Azure release files

Requires:   azure-release-variant = %{version}-%{release}
Suggests:   azure-release

Requires:   azure-repos(%{version})
Requires:   azure-release-identity = %{version}-%{release}

%description common
Release files common to all Editions and Spins of Azure


%if %{with basic}
%package identity-basic
Summary:        Package providing the basic Azure identity

RemovePathPostfixes: .basic
Provides:       azure-release-identity = %{version}-%{release}
Conflicts:      azure-release-identity


%description identity-basic
Provides the necessary files for a basic Azure installation.
%endif


%if %{with cloud}
%package cloud
Summary:        Base package for Azure Cloud-specific default configurations

RemovePathPostfixes: .cloud
Provides:       azure-release = %{version}-%{release}
Provides:       azure-release-variant = %{version}-%{release}
Provides:       system-release
Provides:       system-release(%{version})
Requires:       azure-release-common = %{version}-%{release}

Recommends:     azure-release-identity-cloud


%description cloud
Provides a base package for Azure Cloud-specific configuration files to
depend on.


%package identity-cloud
Summary:        Package providing the identity for Azure Cloud Edition

RemovePathPostfixes: .cloud
Provides:       azure-release-identity = %{version}-%{release}
Conflicts:      azure-release-identity
Requires(meta): azure-release-cloud = %{version}-%{release}


%description identity-cloud
Provides the necessary files for a Azure installation that is identifying
itself as Azure Cloud Edition.
%endif


%if %{with container}
%package container
Summary:        Base package for Azure container specific default configurations

RemovePathPostfixes: .container
Provides:       azure-release = %{version}-%{release}
Provides:       azure-release-variant = %{version}-%{release}
Provides:       system-release
Provides:       system-release(%{version})
Requires:       azure-release-common = %{version}-%{release}

Recommends:     azure-release-identity-container


%description container
Provides a base package for Azure container specific configuration files to
depend on as well as container system defaults.


%package identity-container
Summary:        Package providing the identity for Azure Container Base Image

RemovePathPostfixes: .container
Provides:       azure-release-identity = %{version}-%{release}
Conflicts:      azure-release-identity
Requires(meta): azure-release-container = %{version}-%{release}


%description identity-container
Provides the necessary files for a Azure installation that is identifying
itself as the Azure Container Base Image.
%endif


%prep

%build

%install

# Symlink the -release files
install -d %{buildroot}%{_sysconfdir}
ln -s ../usr/lib/azure-release %{buildroot}%{_sysconfdir}/azure-release
ln -s azure-release %{buildroot}%{_sysconfdir}/mariner-release
ln -s azure-release %{buildroot}%{_sysconfdir}/system-release

cat <<-"EOF" > %{buildroot}%{_libdir}/lsb-release
	DISTRIB_ID="azurelinux"
	DISTRIB_RELEASE="%{dist_version}"
	DISTRIB_CODENAME=AzureLinux
	DISTRIB_DESCRIPTION="Microsoft Azure Linux %{dist_version}"
EOF
ln -s ../usr/lib/lsb-release %{buildroot}%{_sysconfdir}/lsb-release

cat <<-"EOF" > %{buildroot}%{_libdir}/azure-release
	Azure Linux %{dist_version}
	AZURE_BUILD_NUMBER=%{mariner_build_number}
	MARINER_BUILD_NUMBER=%{mariner_build_number}
EOF
ln -s ../usr/lib/azure-release %{buildroot}%{_sysconfdir}/azure-release

cat <<-"EOF" > %{buildroot}%{_libdir}/issue
	Welcome to Azure Linux %{dist_version} (%{_arch}) - Kernel \r (\l)
EOF
ln -s ../usr/lib/issue %{buildroot}%{_sysconfdir}/issue

cat <<-"EOF" %{buildroot}%{_libdir}/issue.net
	Welcome to Azure Linux %{dist_version} (%{_arch})
EOF
ln -s ../usr/lib/issue.net %{buildroot}%{_sysconfdir}/issue.net

# Create /etc/issue.d
mkdir -p %{buildroot}%{_sysconfdir}/issue.d

# Create common os-release
cat <<-"EOF" >> os-release
	NAME="%{dist_name}"
	VERSION="%{dist_version}"
	ID=azurelinux
	VERSION_ID="%{version}"
	PRETTY_NAME="Microsoft Azure Linux %{version}"
	ANSI_COLOR="1;34"
	HOME_URL="%{url}"
	BUG_REPORT_URL="%{url}"
	SUPPORT_URL="%{url}"
EOF

# Create os-release files for the different editions

%if %{with basic}
# Basic
cp -p os-release \
      %{buildroot}%{_libdir}/os-release.basic
%endif

%if %{with cloud}
# Cloud
cp -p os-release \
      %{buildroot}%{_libdir}/os-release.cloud
echo "VARIANT=\"Cloud Edition\"" >> %{buildroot}%{_libdir}/os-release.cloud
echo "VARIANT_ID=cloud" >> %{buildroot}%{_libdir}/os-release.cloud
%endif

%if %{with container}
# Container
cp -p os-release \
      %{buildroot}%{_libdir}/os-release.container
echo "VARIANT=\"Container Image\"" >> %{buildroot}%{_libdir}/os-release.container
echo "VARIANT_ID=container" >> %{buildroot}%{_libdir}/os-release.container
%endif

%if %{with server}
# Server
cp -p os-release \
      %{buildroot}%{_libdir}/os-release.server
echo "VARIANT=\"Server Edition\"" >> %{buildroot}%{_libdir}/os-release.server
echo "VARIANT_ID=server" >> %{buildroot}%{_libdir}/os-release.server
%endif

# Create the symlink for /etc/os-release
ln -s ../usr/lib/os-release %{buildroot}%{_sysconfdir}/os-release

# Set up the dist tag macros
install -d -m 755 %{buildroot}%{_rpmconfigdir}/macros.d
cat <<- "EOF" >> %{buildroot}%{_rpmconfigdir}/macros.d/macros.dist
	# dist macros.

	%%__bootstrap         ~bootstrap
	%%azure               %{dist_version_major}
	%%distcore            .azl%%{azure}
	%%dist                %%{distcore}%%{?with_bootstrap:%%{__bootstrap}}
	%%dist_vendor         %{dist_vendor}
	%%dist_name           %{dist_name}
	%%dist_home_url       %{dist_home_url}
	%%dist_bug_report_url %{dist_home_url}
	%%dist_debuginfod_url %{dist_home_url}
EOF

# Default presets for system and user
install -Dm0644 %{SOURCE1} -t %{buildroot}%{_libdir}/systemd/system-preset/
install -Dm0644 %{SOURCE2} -t %{buildroot}%{_libdir}/systemd/user-preset/

# Default disable presets
install -Dm0644 %{SOURCE3} -t %{buildroot}%{_libdir}/systemd/system-preset/
install -Dm0644 %{SOURCE3} -t %{buildroot}%{_libdir}/systemd/user-preset/


%files common
%defattr(-,root,root,-)
%{_libdir}/azure-release
%{_sysconfdir}/os-release
%{_sysconfdir}/azure-release
%{_sysconfdir}/system-release
%attr(0644,root,root) %{_libdir}/issue
%config(noreplace) %{_sysconfdir}/issue
%attr(0644,root,root) %{_libdir}/issue.net
%config(noreplace) %{_sysconfdir}/issue.net
%dir %{_sysconfdir}/issue.d
%attr(0644,root,root) %{_rpmconfigdir}/macros.d/macros.dist
%dir %{_libdir}/systemd/user-preset/
%{_libdir}/systemd/user-preset/90-default-user.preset
%{_libdir}/systemd/user-preset/99-default-disable.preset
%dir %{_libdir}/systemd/system-preset/
%{_libdir}/systemd/system-preset/90-default.preset
%{_libdir}/systemd/system-preset/99-default-disable.preset


%if %{with basic}
%files
%files identity-basic
%{_libdir}/os-release.basic
%endif


%if %{with cloud}
%files cloud
%files identity-cloud
%{_libdir}/os-release.cloud
%endif


%if %{with container}
%files container
%files identity-container
%{_libdir}/os-release.container
%endif


%if %{with server}
%files server
%files identity-server
%{_libdir}/os-release.server
%endif


%changelog
* Fri Jan 26 15:00:59 EST 2024 Dan Streetman <ddstreet@ieee.org> - 3.0-2
- Add release subpackages

* Wed Nov 29 2023 Jon Slobodzian <joslobo@microsoft.com> - 3.0-1
- First version of Azure Linux 3.0.  Includes minimal rebranding changes.

* Fri Oct 20 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-53
- Bump release for October 2023 Release 2

* Wed Sep 27 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-52
- Bump release for October 2023 Release

* Wed Sep 20 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-51
- Bump release for September 2023 Update 2

* Mon Sep 04 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-50
- Bump release for September 2023 Update

* Mon Aug 21 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-49
- Bump release for August 2023 Release 3

* Thu Aug 10 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-48
- Bump release for August 2023 Release 2

* Thu Aug 10 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-47
- Bump release for August 2023 Update 2

* Fri Aug 04 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-46
- Bump release for August 2023 Release

* Mon Jul 10 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-45
- Bump release for July 2023 Update

* Thu Jun 29 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-44
- Bump release for June 2023 Update 3

* Sun Jun 18 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-43
- Bump release for June 2023 Update 2

* Sat Jun 03 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-42
- Bump release for June 2023 Update

* Fri May 26 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-41
- Bump release for May 2023 Update 2

* Tue May 16 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-40
- Bump release for May 2023 Update

* Tue May 16 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 2.0-39
- Bump release for May 2023 Update

* Sat Apr 22 2023 Jon Slobodzian <joslobo@microsoft.com> - 2.0-38
- Updating version for April update 2

* Thu Apr 06 2023 Jon Slobodzian <joslobo@microsoft.com> - 2.0-37
- Updating version for April update.

* Fri Mar 17 2023 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0-36
- Updating version for March 2023 update 2.

* Thu Mar 02 2023 Andrew Phelps <anphel@microsoft.com> - 2.0-35
- Updating version for March 2023 update 1.

* Tue Feb 14 2023 Jon Slobodzian <joslobo@microsoft.com> - 2.0-34
- Updating version for February update 2.

* Tue Feb 07 2023 Jon Slobodzian <joslobo@microsoft.com> - 2.0-33
- Updating version for February update.

* Tue Jan 24 2023 Jon Slobodzian <joslobo@microsoft.com> - 2.0-32
- Updating version for January update 2.

* Thu Jan 05 2023 Jon Slobodzian <joslobo@microsoft.com> - 2.0-31
- Updating version for January update.

* Mon Dec 19 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-30
- Updating version for December update 3.

* Sat Dec 10 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-29
- Updating version for December update 2.

* Thu Dec 01 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-28
- Updating version for December update.

* Mon Nov 21 2022 Mandeep Plaha <mandeepplaha@microsoft.com> - 2.0.27
- Updating version for November update 2.

* Wed Nov 09 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-26
- Updating version for November update.

* Sat Oct 29 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0-25
- Updating version for a full October release.

* Tue Oct 25 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0-24
- Updating version for October update.

* Fri Oct 07 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0-23
- Updating version for October release.

* Fri Sep 23 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-22
- Updating version for September update 3.

* Fri Sep 16 2022 Andrew Phelps <anphel@microsoft.com> - 2.0.21
- Updating version for September update 2.

* Thu Sep 08 2022 Minghe Ren <mingheren@microsoft.com> - 2.0-20
- remove issue.net kernel part as sshd doesn't support the old-style telnet escape sequences

* Thu Sep 08 2022 Andrew Phelps <anphel@microsoft.com> - 2.0-19
- Updating version for September CVE update.

* Tue Aug 16 2022 Andrew Phelps <anphel@microsoft.com> - 2.0-18
- Updating version for August update 2.

* Wed Aug 03 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0-17
- Updating version for August update.

* Tue Jul 26 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0-16
- Updating version for July update 2.

* Fri Jul 08 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-15
- Updating version for July update.

* Sat Jun 25 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-14
- Updating version for June update 2.

* Wed Jun 08 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-13
- Updating version for June update.

* Sat May 21 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-12
- Updating version for May update.

* Tue Apr 19 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-11
- Updating version for GA Release Candidate

* Sat Apr 16 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-10
- Updating version for Preview-H Release.

* Sat Apr 09 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-9
- Updating version for Preview-G Release.

* Wed Mar 30 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-8
- Updating version for Preview-F Release.

* Fri Mar 4 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-7
- Updating version for Preview-E Release

* Thu Feb 24 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0-6
- Surrounding 'VERSION_ID' inside 'os-release' with double quotes.

* Sun Feb 06 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-5
- Updating version for Preview D-Release

* Wed Jan 19 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-4
- CBL-Mariner 2.0 Public Preview C Release.
- License verified

* Thu Dec 16 2021 Jon Slobodzian <joslobo@microsoft.com> - 2.0-3
- CBL-Mariner 2.0 Public Preview B Release version with fixed repo configuration files.

* Mon Dec 13 2021 Jon Slobodzian <joslobo@microsoft.com> - 2.0-2
- CBL-Mariner 2.0 Public Preview A Release version.

* Thu Jul 29 2021 Jon Slobodzian <joslobo@microsoft.com> - 2.0-1
- Updating version and distrotag for future looking 2.0 branch.  Formatting fixes.
- Remove %%clean section, buildroot cleaning step (both automatically done by RPM)

* Wed Apr 27 2021 Jon Slobodzian <joslobo@microsoft.com> - 1.0-16
- Updating version for April update

* Tue Mar 30 2021 Jon Slobodzian <joslobo@microsoft.com> - 1.0-15
- Updating version for March update

* Mon Feb 22 2021 Jon Slobodzian <joslobo@microsoft.com> - 1.0-14
- Updating version for February update

* Sun Jan 24 2021 Jon Slobodzian <joslobo@microsoft.com> - 1.0-13
- Updating version for January update

* Mon Dec 21 2020 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.0-12
- Updating version for December update.

* Fri Nov 20 2020 Nicolas Guibourge <nicolasg@microsoft.com> - 1.0-11
- Updating version for November update

* Sat Oct 24 2020 Jon Slobodzian <joslobo@microsoft.com> - 1.0-10
- Updating version for October update

* Fri Sep 04 2020 Mateusz Malisz <mamalisz@microsoft.com> - 1.0-9
- Remove empty %%post section, dropping dependency on /bin/sh

* Tue Aug 24 2020 Jon Slobodzian <joslobo@microsoft.com> - 1.0-8
- Changing CBL-Mariner ID from "Mariner" to "mariner" to conform to standard.  Also updated Distrib-Description and Name per internal review.

* Tue Aug 18 2020 Jon Slobodzian <joslobo@microsoft.com> - 1.0-7
- Restoring correct Name, Distribution Name, CodeName and ID.

* Fri Jul 31 2020 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.0-6
- Updating distribution name.

* Wed Jul 29 2020 Nick Samson <nisamson@microsoft.com> - 1.0-5
- Updated os-release file and URL to reflect project naming

* Wed Jun 24 2020 Jon Slobodzian <joslobo@microsoft.com> - 1.0-4
- Updated license for 1.0 release.

* Mon May 04 2020 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.0-3
- Providing "system-release(releasever)" for the sake of DNF
- and other package management tools.

* Thu Jan 30 2020 Jon Slobodzian <joslobo@microsoft.com> 1.0-2
- Remove Microsoft name from distro version.

* Wed Sep 04 2019 Mateusz Malisz <mamalisz@microsoft.com> 1.0-1
- Original version for CBL-Mariner.
