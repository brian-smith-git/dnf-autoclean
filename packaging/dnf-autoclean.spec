Name:           dnf-autoclean
Version:        1.0.0
Release:        1%{?dist}
Summary:        Automatic cleanup tool for Fedora kernels and orphan packages

License:        MIT
URL:            https://github.com/brian-smith-git/dnf-autoclean
Source0:        %{name}-%{version}.tar.gz

Requires:       dnf, python3, polkit

%description
DNF AutoClean automatically removes old kernels, orphan packages, and runs autoremove.
Includes systemd timer, polkit integration, and GTK GUI.

%install
mkdir -p %{buildroot}/usr/local/bin
install -m 755 dnf-autoclean.py %{buildroot}/usr/local/bin/
install -m 755 dnf-autoclean-gui.py %{buildroot}/usr/local/bin/

mkdir -p %{buildroot}/etc/systemd/system
install -m 644 dnf-autoclean.service %{buildroot}/etc/systemd/system/
install -m 644 dnf-autoclean.timer %{buildroot}/etc/systemd/system/

mkdir -p %{buildroot}/usr/share/applications
install -m 644 dnf-autoclean.desktop %{buildroot}/usr/share/applications/

mkdir -p %{buildroot}/usr/share/metainfo
install -m 644 dnf-autoclean.metainfo.xml %{buildroot}/usr/share/metainfo/

mkdir -p %{buildroot}/usr/share/polkit-1/actions
install -m 644 org.brian-smith.dnf-autoclean.policy %{buildroot}/usr/share/polkit-1/actions/

%files
/usr/local/bin/*
/etc/systemd/system/dnf-autoclean.service
/etc/systemd/system/dnf-autoclean.timer
/usr/share/applications/dnf-autoclean.desktop
/usr/share/metainfo/dnf-autoclean.metainfo.xml
/usr/share/polkit-1/actions/org.brian-smith.dnf-autoclean.policy

%changelog
* Sat Sep 27 2025 Brian Smith <brian-smith-git> - 1.0.0-1
- Initial release
