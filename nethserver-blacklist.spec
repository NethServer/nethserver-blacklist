Summary: NethServer blacklist
Name: nethserver-blacklist
Version: 1.2.0
Release: 1%{?dist}
License: GPL
Source0: %{name}-%{version}.tar.gz
# Build Source1 by executing prep-sources
Source1: %{name}-ui.tar.gz

BuildArch: noarch

Requires: git
Requires: nethserver-firewall-base
Requires: pihole-ftl

BuildRequires: nethserver-devtools

%description
Blacklist module for NethServer.


%prep
%setup -q

%build
perl createlinks
sed -i 's/_RELEASE_/%{version}/' %{name}.json

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/usr/share/cockpit/%{name}/
mkdir -p %{buildroot}/usr/share/cockpit/nethserver/applications/
mkdir -p %{buildroot}/usr/libexec/nethserver/api/%{name}/
tar xf %{SOURCE1} -C %{buildroot}/usr/share/cockpit/%{name}/
cp -a %{name}.json %{buildroot}/usr/share/cockpit/nethserver/applications/
cp -a api/* %{buildroot}/usr/libexec/nethserver/api/%{name}/

(cd root ; find . -depth -print | cpio -dump %{buildroot})
%{genfilelist} %{buildroot} --file /etc/sudoers.d/50_nsapi_nethserver_blacklist 'attr(0440,root,root)' > %{name}-%{version}-%{release}-filelist
echo "%doc COPYING" >> %{name}-%{version}-%{release}-filelist


%post

%preun

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}-%{version}-%{release}-filelist
%defattr(-,root,root)
%dir %{_nseventsdir}/%{name}-update
/usr/libexec/nethserver/api/%{name}/

%changelog
* Wed Mar 17 2021 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.2.0-1
- Blacklist: add geoIP support - NethServer/dev#6458

* Mon Mar 15 2021 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.1.8-1
- DNS Blacklists for threat shield does not start correctly after a disaster recovery - Bug NethServer/dev#6455

* Thu Mar 11 2021 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.1.7-1
- Threat shield: Domain check tool always shows all clients - Bug NethServer/dev#6448

* Wed Mar 03 2021 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.1.6-1
- Threat shield can't be enabled - Bug NethServer/dev#6444

* Mon Jan 11 2021 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.1.5-1
- UI issue on tables using vue-good-table - Bug NethServer/dev#6390

* Wed Dec 16 2020 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.1.4-1
- Blacklist: increase the maxelem set of ipset - NethServer/dev#6359

* Thu Jul 16 2020 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.1.3-1
- Threat shield: Cannot load IP blacklist logs in Analysis page - Bug NethServer/dev#6229

* Thu Jul 09 2020 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.1.2-1
- Blacklist: log rotate error on /var/log/pihole-FTL.log - Bug NethServer/dev#6226

* Tue Jul 07 2020 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.1.1-1
- DNS Blacklists for threat shield   - NethServer/dev#6212

* Thu Jul 02 2020 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.1.0-1
- DNS Blacklists for threat shield   - NethServer/dev#6212
- Human readable numbers in Cockpit dashboards - NethServer/dev#6206

* Tue Jun 16 2020 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.0.7-1
- Threat shield: improve first download time - NethServer/dev#6207

* Mon Jun 15 2020 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.0.6-1
- Firewall: Prevent object deletion if used in Threat Shield whitelist - Bug NethServer/dev#6196

* Fri May 29 2020 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.0.5-1
- Threat Shield: weird analysis page layout after update - Bug NethServer/dev#6188

* Fri May 22 2020 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.0.4-1
- UI enhancements on Threat Shield - NethServer/dev#6171

* Tue Apr 28 2020 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.0.3-1
- Threat Shield: cannot sort by category status - NethServer/dev#6140

* Thu Apr 09 2020 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.0.2-1
- Threat shield: check IP address by clicking on recent logs entries - NethServer/dev#6123

* Wed Apr 01 2020 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.0.1-1
- Blacklist: systemd logs ignoring a conf - Bug NethServer/dev#6104

* Tue Mar 24 2020 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.0.0-1
- Blacklist support (threat shield) - NethServer/dev#6072

