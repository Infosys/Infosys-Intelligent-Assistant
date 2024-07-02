/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { NgModule } from '@angular/core';
import { CommonModule, } from '@angular/common';
import { BrowserModule  } from '@angular/platform-browser';
import { Routes, RouterModule } from '@angular/router';
import { LoginComponent } from './login-page/login-page.component';
import { AdminLayoutComponent } from './layouts/admin-layout/admin-layout.component';
import {BotImageUploadComponent} from './other-training/BOT-imageupload/BOT-imageupload.component';
import { AuthComponent } from './auth/auth.component';
const routes: Routes =[
  { path : 'auth', component: AuthComponent},
  {
  path: '',
  redirectTo: 'login',
  pathMatch: 'full',
}, {
  path: '',
  component: AdminLayoutComponent,
  children: [{
    path: '',
    loadChildren: './layouts/admin-layout/admin-layout.module#AdminLayoutModule'
}]
},
    { path : 'login' , component: LoginComponent },
    {path:'imageUploadScreen/:workflowname/:taskname',component : BotImageUploadComponent},
];
@NgModule({
  imports: [
    CommonModule,
    BrowserModule,
    RouterModule.forRoot(routes,{useHash:true })
  ],
  exports: [
  ],
})
export class AppRoutingModule { }
