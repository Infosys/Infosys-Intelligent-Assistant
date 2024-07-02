/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, ElementRef } from '@angular/core';
import { ROUTES } from '../sidebar/sidebar.component';
import { Location, LocationStrategy, PathLocationStrategy } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
declare var $: any;
@Component({
    selector: 'app-navbar',
    templateUrl: './navbar.component.html',
    styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {
    private listTitles: any[];
    location: Location;
    mobile_menu_visible: any = 0;
    private toggleButton: any;
    private sidebarVisible: boolean;
    sso: boolean = false
    constructor(location: Location, private element: ElementRef, private router: Router, private httpClinet: HttpClient) {
        this.location = location;
        this.sidebarVisible = false;
    }
    goBack() {
        this.location.back(); // <-- go back to previous location on cancel
    }
    goForward() {
        this.location.forward();
    }
    ngOnInit() {
        this.sso = (localStorage.getItem('sso') == 'true') ? true : false
        console.log('sso:' + this.sso)
        const btnunhide = document.getElementsByClassName('btn-unhide') as HTMLCollectionOf<HTMLElement>;
        btnunhide[0].style.display = 'none';
        this.listTitles = ROUTES.filter(listTitle => listTitle);
        const navbar: HTMLElement = this.element.nativeElement;
        this.toggleButton = navbar.getElementsByClassName('navbar-toggler')[0];
        this.router.events.subscribe((event) => {
            this.sidebarClose();
            var $layer: any = document.getElementsByClassName('close-layer')[0];
            if ($layer) {
                $layer.remove();
                this.mobile_menu_visible = 0;
            }
        });
    }
    sidebarOpen() {
        const toggleButton = this.toggleButton;
        const body = document.getElementsByTagName('body')[0];
        setTimeout(function () {
            toggleButton.classList.add('toggled');
        }, 500);
        body.classList.add('nav-open');
        this.sidebarVisible = true;
    };
    sidebarClose() {
        const body = document.getElementsByTagName('body')[0];
        this.toggleButton.classList.remove('toggled');
        this.sidebarVisible = false;
        body.classList.remove('nav-open');
    };
    sidebarToggle() {
        var $toggle = document.getElementsByClassName('navbar-toggler')[0];
        if (this.sidebarVisible === false) {
            this.sidebarOpen();
        } else {
            this.sidebarClose();
        }
        const body = document.getElementsByTagName('body')[0];
        if (this.mobile_menu_visible == 1) {
            // $('html').removeClass('nav-open');
            body.classList.remove('nav-open');
            if ($layer) {
                $layer.remove();
            }
            setTimeout(function () {
                $toggle.classList.remove('toggled');
            }, 400);
            this.mobile_menu_visible = 0;
        } else {
            setTimeout(function () {
                $toggle.classList.add('toggled');
            }, 430);
            var $layer = document.createElement('div');
            $layer.setAttribute('class', 'close-layer');
            if (body.querySelectorAll('.main-panel')) {
                document.getElementsByClassName('main-panel')[0].appendChild($layer);
            } else if (body.classList.contains('off-canvas-sidebar')) {
                document.getElementsByClassName('wrapper-full-page')[0].appendChild($layer);
            }
            setTimeout(function () {
                $layer.classList.add('visible');
            }, 100);
            $layer.onclick = function () { //asign a function
                body.classList.remove('nav-open');
                this.mobile_menu_visible = 0;
                $layer.classList.remove('visible');
                setTimeout(function () {
                    $layer.remove();
                    $toggle.classList.remove('toggled');
                }, 400);
            }.bind(this);
            body.classList.add('nav-open');
            this.mobile_menu_visible = 1;
        }
    };
    compressSidebar() {
        const mainpanel = document.getElementsByClassName('main-panel') as HTMLCollectionOf<HTMLElement>;
        const sidebar = document.getElementsByClassName('sidebar') as HTMLCollectionOf<HTMLElement>;
        const btnhide = document.getElementsByClassName('btn-hide') as HTMLCollectionOf<HTMLElement>;
        const btnunhide = document.getElementsByClassName('btn-unhide') as HTMLCollectionOf<HTMLElement>;
        mainpanel[0].style.width = '100%';
        sidebar[0].style.display = 'none';
        btnhide[0].style.display = 'none';
        btnunhide[0].style.display = 'block';
    };
    decompressSidebar() {
        const mainpanel = document.getElementsByClassName('main-panel') as HTMLCollectionOf<HTMLElement>;
        const sidebar = document.getElementsByClassName('sidebar') as HTMLCollectionOf<HTMLElement>;
        const btnunhide = document.getElementsByClassName('btn-unhide') as HTMLCollectionOf<HTMLElement>;
        const btnhide = document.getElementsByClassName('btn-hide') as HTMLCollectionOf<HTMLElement>;
        sidebar[0].style.display = 'block';
        mainpanel[0].style.width = 'calc(100% - 260px)';
        btnunhide[0].style.display = 'none';
        btnhide[0].style.display = 'block';
    };
    getTitle() {
        var titlee;
        if (localStorage.getItem('Access') == 'Admin') {
            titlee = 'Admin'
        } else if (localStorage.getItem('Access') == 'User') {
            titlee = 'User'
        } else {
            titlee = this.location.prepareExternalUrl(this.location.path());
            if (titlee.charAt(0) === '#') {
                titlee = titlee.slice(2);
            }
            titlee = titlee.split('/').pop();
            for (var item = 0; item < this.listTitles.length; item++) {
                if (this.listTitles[item].path === titlee) {
                    return this.listTitles[item].title;
                }
            }
        }
        return (titlee);
    }
    logout() {
        if (localStorage.getItem('sso') == 'true') {
            this.httpClinet.post('/api/logout', null, { responseType: 'json' }).subscribe(function (data) {
                if (data[0]['Status'] == 'logout') {
                    localStorage.clear();
                    sessionStorage.clear();
                    window.location.href = data[0]['Link']
                }
                else {
                    alert('could not logout! try again later');
                }
            }, function (err) {
                console.log('error occured! please try again later');
            });
        }
        else {
            this.httpClinet.post('/api/logout', null, { responseType: 'text' }).subscribe(data => {
                if (data) {
                    localStorage.clear();
                    this.router.navigate(['/login']);
                    if (data == 'Successfully logged out') {
                        console.log('logged out successfully from backend');
                    } else {
                        console.log('could not find any longin');
                    }
                } else {
                    alert('could not logout! try again later');
                }
            }, err => {
                console.log('error occured! please try again later');
            });
        }
    }
}
