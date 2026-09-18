import sys
import os
import objc

from Foundation import NSObject
from AppKit import (
    NSApplication,
    NSApplicationActivationPolicyAccessory,
    NSWindow,
    NSButton,
    NSTextField,
    NSImage,
    NSImageView,
    NSMakeRect,
    NSBackingStoreBuffered,
    NSWindowStyleMaskTitled,
    NSWindowStyleMaskClosable,
    NSWindowStyleMaskResizable,
    NSCenterTextAlignment,
    NSFont
)

degiskenler = {}


def deger_al(deger):
    deger = deger.strip()

    if deger.startswith('"') and deger.endswith('"'):
        return deger[1:-1]

    if deger.isdigit():
        return int(deger)

    if deger in degiskenler:
        return degiskenler[deger]

    return deger


def kosul_kontrol(kosul):
    for operator in [">=", "<=", "==", "!=", ">", "<"]:
        if operator in kosul:

            sol, sag = kosul.split(operator, 1)

            sol = deger_al(sol)
            sag = deger_al(sag)

            if operator == ">=":
                return sol >= sag
            if operator == "<=":
                return sol <= sag
            if operator == "==":
                return sol == sag
            if operator == "!=":
                return sol != sag
            if operator == ">":
                return sol > sag
            if operator == "<":
                return sol < sag

    return False


def blok_al(kod, baslangic):
    blok = []
    i = baslangic

    while i < len(kod):

        satir = kod[i].strip()

        if satir == "}":
            return blok, i

        if satir:
            blok.append(satir)

        i += 1

    return blok, i


def blok_calistir(blok):
    for komut in blok:
        komut_calistir(komut)


def komut_calistir(satir):

    satir = satir.strip()

    if not satir:
        return

    # YAZ
    if satir.startswith("yaz "):
        print(deger_al(satir[4:]))
        return

    # DEĞİŞKEN
    if "=" in satir:
        isim, deger = satir.split("=", 1)

        degiskenler[isim.strip()] = deger_al(deger)

        return


class PoseidonButon(NSObject):

    def initWithBlok_(self, blok):

        self = objc.super(
            PoseidonButon,
            self
        ).init()

        if self:
            self.blok = blok

        return self

    def tikla_(self, sender):

        print("Poseidon: Butona basıldı!")

        blok_calistir(self.blok)


class PoseidonPencere:

    def __init__(self, baslik, blok):

        self.app = NSApplication.sharedApplication()

        self.app.setActivationPolicy_(
            NSApplicationActivationPolicyAccessory
        )

        self.butons = []

        self.pencere_olustur(
            baslik,
            blok
        )

    def pencere_olustur(self, baslik, blok):

        stil = (
            NSWindowStyleMaskTitled |
            NSWindowStyleMaskClosable |
            NSWindowStyleMaskResizable
        )

        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 650, 650),
            stil,
            NSBackingStoreBuffered,
            False
        )

        self.window.setTitle_(baslik)

        self.window.center()

        self.window.setReleasedWhenClosed_(False)

        view = self.window.contentView()

        y = 560

        resim_dosyasi = None

        # Önce pencere içeriğini oku
        i = 0

        while i < len(blok):

            satir = blok[i]

            # RESİM
            if satir.startswith("resim "):

                dosya = deger_al(
                    satir[6:]
                )

                if not os.path.isabs(dosya):

                    dosya = os.path.join(
                        os.path.dirname(
                            os.path.abspath(
                                sys.argv[1]
                            )
                        ),
                        dosya
                    )

                resim_dosyasi = dosya

            # METİN
            elif satir.startswith("metin "):

                metin = deger_al(
                    satir[6:]
                )

                label = NSTextField.alloc().initWithFrame_(
                    NSMakeRect(
                        75,
                        y,
                        500,
                        45
                    )
                )

                label.setStringValue_(
                    str(metin)
                )

                label.setBezeled_(False)
                label.setDrawsBackground_(False)
                label.setEditable_(False)
                label.setSelectable_(False)

                label.setAlignment_(
                    NSCenterTextAlignment
                )

                label.setFont_(
                    NSFont.systemFontOfSize_(22)
                )

                view.addSubview_(label)

                y -= 65

            # BUTON
            elif satir.startswith("buton "):

                yazi = satir[6:].strip()

                # Eğer butonun arkasından { geliyorsa
                if yazi.endswith("{"):

                    yazi = yazi[:-1].strip()

                    yazi = deger_al(yazi)

                    alt_blok = []

                    i += 1

                    while i < len(blok):

                        alt_satir = blok[i]

                        if alt_satir == "}":
                            break

                        alt_blok.append(
                            alt_satir
                        )

                        i += 1

                else:

                    yazi = deger_al(
                        yazi
                    )

                    alt_blok = []

                hedef = PoseidonButon.alloc().initWithBlok_(
                    alt_blok
                )

                buton = NSButton.alloc().initWithFrame_(
                    NSMakeRect(
                        225,
                        y,
                        200,
                        45
                    )
                )

                buton.setTitle_(
                    str(yazi)
                )

                buton.setTarget_(
                    hedef
                )

                buton.setAction_(
                    "tikla:"
                )

                view.addSubview_(
                    buton
                )

                self.butons.append(
                    hedef
                )

                y -= 65

            # YAZ
            elif satir.startswith("yaz "):

                print(
                    deger_al(
                        satir[4:]
                    )
                )

            i += 1

        # RESMİ EN SON EKLE
        if resim_dosyasi:

            if os.path.exists(
                resim_dosyasi
            ):

                image = NSImage.alloc().initWithContentsOfFile_(
                    resim_dosyasi
                )

                image_view = NSImageView.alloc().initWithFrame_(
                    NSMakeRect(
                        75,
                        120,
                        500,
                        350
                    )
                )

                image_view.setImage_(
                    image
                )

                view.addSubview_(
                    image_view
                )

            else:

                print(
                    "Resim bulunamadı:",
                    resim_dosyasi
                )

        self.window.makeKeyAndOrderFront_(
            None
        )

        self.app.activateIgnoringOtherApps_(
            True
        )

        self.app.run()


def poseidon_calistir(dosya):

    with open(
        dosya,
        "r",
        encoding="utf-8"
    ) as f:

        kod = [
            satir.strip()
            for satir in f.readlines()
        ]

    i = 0

    while i < len(kod):

        satir = kod[i]

        if not satir or satir.startswith("#"):

            i += 1
            continue

        # PENCERE
        if satir.startswith(
            "pencere "
        ):

            baslik = satir[8:].strip()

            if baslik.endswith("{"):

                baslik = baslik[:-1].strip()

            baslik = deger_al(
                baslik
            )

            i += 1

            blok, i = blok_al(
                kod,
                i
            )

            PoseidonPencere(
                baslik,
                blok
            )

            return

        komut_calistir(
            satir
        )

        i += 1


if len(sys.argv) < 2:

    print(
        "Kullanım: python3 poseidon.py program.pos"
    )

else:

    poseidon_calistir(
        sys.argv[1]
    )