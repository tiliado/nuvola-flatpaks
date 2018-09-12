GNOME_VERSION := 3.28

info:
	cat Makefile

dnf-install-flatpak:
	dnf -y update
	dnf install -y flatpak flatpak-builder
	dnf clean all

install-deps:
	flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
	flatpak install -y --subpath= flathub \
		org.gnome.Sdk//$(GNOME_VERSION) \
		org.gnome.Sdk.Debug//$(GNOME_VERSION) \
		org.gnome.Sdk.Locale//$(GNOME_VERSION) \
		org.gnome.Sdk.Docs//$(GNOME_VERSION) \
		org.gnome.Platform.Locale//$(GNOME_VERSION) \
		org.freedesktop.Platform.html5-codecs \
		> /dev/null

build:
	rm -rf result
	time flatpak-builder result eu.tiliado.NuvolaSdk.yaml
