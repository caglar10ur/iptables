#
# $Id: iproute.spec 7668 2008-01-08 11:49:43Z thierry $
#
%define url $URL: svn+ssh://thierry@svn.planet-lab.org/svn/iproute2/trunk/iproute.spec $

%define name iptables
%define version 1.4.1.1
%define taglevel 1

%define release %{taglevel}%{?pldistro:.%{pldistro}}%{?date:.%{date}}

Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab %{plrelease}
URL: %(echo %{url} | cut -d ' ' -f 2)

%define build_devel 1
%define linux_header 0

Summary: Tools for managing Linux kernel packet filtering capabilities.
Name: %{name}
Version: %{version}
Release: %{release}
Source: http://www.netfilter.org/%{name}-%{version}.tar.bz2
%define SOURCE1 iptables.init
%define SOURCE2 iptables-config
%define SOURCE3 planetlab-config
Group: System Environment/Base
#URL: http://www.netfilter.org/
BuildRoot: %{_tmppath}/%{name}-buildroot
License: GPL
BuildPrereq: /usr/bin/perl
Requires: kernel >= 2.6.27
Requires(post,postun): chkconfig
Prefix: %{_prefix}
BuildRequires: kernel-devel

%package ipv6
Summary: IPv6 support for iptables.
Group: System Environment/Base
Requires: %{name} = %{version}

%if %{build_devel}
%package devel
Summary: Development package for iptables.
Group: System Environment/Base
Requires: %{name} = %{version}
%endif

%description
The iptables utility controls the network packet filtering code in the
Linux kernel. If you need to set up firewalls and/or IP masquerading,
you should install this package.

%description ipv6
The iptables package contains IPv6 (the next version of the IP
protocol) support for iptables. Iptables controls the Linux kernel
network packet filtering code, allowing you to set up firewalls and IP
masquerading. 

Install iptables-ipv6 if you need to set up firewalling for your
network and you are using ipv6.

%if %{build_devel}
%description devel
The iptables utility controls the network packet filtering code in the
Linux kernel. If you need to set up firewalls and/or IP masquerading,
you should install this package.
%endif

%prep
rm -rf %{buildroot}

%setup -q

# Put it to a reasonable place
find . -type f -exec perl -pi -e "s,/usr,%{prefix},g" {} \;

%build
TOPDIR=`pwd`
OPT="$RPM_OPT_FLAGS -I$TOPDIR/include"

%define KERNEL %(rpm -q --qf '%%{VERSION}-%%{RELEASE}-%%{ARCH}\\n' kernel-devel | tail -n 1 )
count=$(rpm -q kernel-devel| wc -l)
if [ $count -gt 1 ] ; then
	echo "WARNING: choosing kernel-devel-%{KERNEL}"
	echo "  but there are other kernel-devel packages installed: $(rpm -q kernel-devel)"
fi
	
%define KERNEL_DIR "/usr/src/kernels/%{KERNEL}"

%if %{build_devel}
%define configure_option --enable-devel
%else
%define configure_option
%endif

./configure --prefix=/usr %{configure_option} --enable-libipq --bindir=/bin --sbindir=/sbin --sysconfdir=/etc --libdir=/%{_libdir} --libexecdir=/%{_lib} --mandir=%{_mandir} --includedir=%{_includedir}

make COPT_FLAGS="$OPT" KERNEL_DIR=%{KERNEL_DIR} LIBDIR=/%{_lib}

%install
# Thierry : for 1.4.1.1
# from http://fr2.rpmfind.net/linux/fedora/releases/10/Everything/source/SRPMS/iptables-1.4.1.1-2.fc10.src.rpm
make install DESTDIR=%{buildroot} 

# install iptc devel library
%if %{build_devel}
install -m 644 libiptc/libiptc.a %{buildroot}/%{_libdir}
%endif

# install init scripts and configuration files
install -d -m 755 $RPM_BUILD_ROOT/etc/rc.d/init.d
install -c -m 755 %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/iptables
sed -e 's;iptables;ip6tables;g' -e 's;IPTABLES;IP6TABLES;g' < %{SOURCE1} > ip6tables.init
install -c -m 755 ip6tables.init $RPM_BUILD_ROOT/etc/rc.d/init.d/ip6tables
install -d -m 755 $RPM_BUILD_ROOT/etc/sysconfig
install -c -m 755 %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/iptables-config
sed -e 's;iptables;ip6tables;g' -e 's;IPTABLES;IP6TABLES;g' < %{SOURCE2} > ip6tables-config
install -c -m 755 ip6tables-config $RPM_BUILD_ROOT/etc/sysconfig/ip6tables-config
install -c -m755 %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/iptables

%clean
rm -rf $RPM_BUILD_ROOT 

%post
/sbin/chkconfig --add iptables
if [ "$PL_BOOTCD" != "1" ] ; then
    /sbin/service iptables restart
fi

%preun
if [ "$1" = 0 ]; then
    /sbin/chkconfig --del iptables
fi

%post ipv6
/sbin/chkconfig --add ip6tables
if [ "$PL_BOOTCD" != "1" ] ; then
    /sbin/service ip6tables restart
fi

%preun ipv6
if [ "$1" = 0 ]; then
    /sbin/chkconfig --del ip6tables
fi

%files
%defattr(-,root,root,0755)
%doc COPYING INSTALL INCOMPATIBILITIES
%config %attr(0755,root,root) /etc/rc.d/init.d/iptables
%config(noreplace) %attr(0600,root,root) /etc/sysconfig/iptables-config
%config(noreplace) %attr(0600,root,root) /etc/sysconfig/iptables
/sbin/iptables*
%{_mandir}/man8/iptables*

# Thierry - WARNING : location changed
%dir /%{_lib}/xtables
# WARNING : location changed
/%{_lib}/xtables/libipt*
# WARNING : new stuff
/%{_lib}/xtables/libxt*
# WARNING : not found at all
#/sbin/ipset*
#%{_mandir}/man8/ipset*
#%dir /%{_lib}/ipset
#/%{_lib}/ipset/libipset*

%files ipv6
%defattr(-,root,root,0755)
%config %attr(0755,root,root) /etc/rc.d/init.d/ip6tables
%config(noreplace) %attr(0600,root,root) /etc/sysconfig/ip6tables-config
/sbin/ip6tables*
# Thierry - WARNING : new stuff
/bin/iptables-xml
%{_mandir}/man8/ip6tables*
# WARNING : location changed
/%{_lib}/xtables/libip6t*

%if %{build_devel}
%files devel
%defattr(-,root,root,0755)
%{_includedir}/*.h
%dir %{_includedir}/libiptc
%{_includedir}/libiptc/*.h
%{_libdir}/libipq.a
%{_libdir}/libiptc.a
%{_mandir}/man3/*
%endif

%changelog
* Sun May 31 2009 Sapan Bhatia <sapanb@cs.princeton.edu> - iptables-1.4.1.1-1

* Sun Feb 22 2009 Sapan Bhatia <sapanb@cs.princeton.edu>
- Checking in initial version of iptables 1.4.1.1
