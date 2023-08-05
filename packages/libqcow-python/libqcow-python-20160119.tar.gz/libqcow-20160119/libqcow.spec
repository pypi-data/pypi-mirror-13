Name: libqcow
Version: 20160119
Release: 1
Summary: Library to access the QEMU Copy-On-Write (QCOW) image file format
Group: System Environment/Libraries
License: LGPL
Source: %{name}-%{version}.tar.gz
URL: https://github.com/libyal/libqcow/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires:         openssl       zlib
BuildRequires:         openssl-devel       zlib-devel

%description
libqcow is a library to access the QEMU Copy-On-Write (QCOW) image file format

%package devel
Summary: Header files and libraries for developing applications for libqcow
Group: Development/Libraries
Requires: libqcow = %{version}-%{release} fuse-libs
BuildRequires: fuse-devel

%description devel
Header files and libraries for developing applications for libqcow.

%package tools
Summary: Several tools for reading QEMU Copy-On-Write (QCOW) image files
Group: Applications/System
Requires: libqcow = %{version}-%{release}  fuse-libs
BuildRequires: fuse-devel

%description tools
Several tools for reading QEMU Copy-On-Write (QCOW) image files

%package python
Summary: Python 2 bindings for libqcow
Group: System Environment/Libraries
Requires: libqcow = %{version}-%{release} python
BuildRequires: python-devel

%description python
Python 2 bindings for libqcow

%package python3
Summary: Python 3 bindings for libqcow
Group: System Environment/Libraries
Requires: libqcow = %{version}-%{release} python3
BuildRequires: python3-devel

%description python3
Python 3 bindings for libqcow

%prep
%setup -q

%build
%configure --prefix=/usr --libdir=%{_libdir} --mandir=%{_mandir} --enable-python2 --enable-python3
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
%make_install

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING NEWS README
%attr(755,root,root) %{_libdir}/*.so.*

%files devel
%defattr(644,root,root,755)
%doc AUTHORS COPYING NEWS README ChangeLog
%{_libdir}/*.a
%{_libdir}/*.la
%{_libdir}/*.so
%{_libdir}/pkgconfig/libqcow.pc
%{_includedir}/*
%{_mandir}/man3/*

%files tools
%defattr(644,root,root,755)
%doc AUTHORS COPYING NEWS README
%attr(755,root,root) %{_bindir}/qcowinfo
%attr(755,root,root) %{_bindir}/qcowmount
%{_mandir}/man1/*

%files python
%defattr(644,root,root,755)
%doc AUTHORS COPYING NEWS README
%{_libdir}/python2*/site-packages/*.a
%{_libdir}/python2*/site-packages/*.la
%{_libdir}/python2*/site-packages/*.so

%files python3
%defattr(644,root,root,755)
%doc AUTHORS COPYING NEWS README
%{_libdir}/python3*/site-packages/*.a
%{_libdir}/python3*/site-packages/*.la
%{_libdir}/python3*/site-packages/*.so

%changelog
* Tue Jan 19 2016 Joachim Metz <joachim.metz@gmail.com> 20160119-1
- Auto-generated

