/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { config } from '../config';
import { locale } from 'moment';
@Component({
    selector : 'app-login',
    templateUrl : 'login-page.component.html',
    styleUrls : ['login-page.component.css']
})
export class LoginComponent implements OnInit {
    errorMessage : boolean;
    username : string;
    password : string;
    oldPassword : string;
    newPassword : string;
    re_enterPassword : string;
    message : string;
    loginType : string = 'login';
    sso:boolean = false;
    passwordFormat:any;  
    constructor( private router: Router, private httpClient: HttpClient ) {}
    ngOnInit() {
    const headerDict = {
        'Accept': 'application/json'
      }
      const requestOptions = {                                                                                                                                                                                 
        headers: new HttpHeaders(headerDict), 
      };
    this.httpClient.post('/api/getconfig', null , 
    { responseType : 'json' }).subscribe(data=>{
        if (data[0]['Status'] == 'Success') {
            let login_status = ""
            this.httpClient.get('/api/loginState', {responseType : 'text'}).subscribe(data => {
                login_status = data
                if (login_status=='No Login Found')
                {
                    localStorage.clear();
                    sessionStorage.clear();
                    this.router.navigate(['/login']);
                }
                else if (login_status == 'Logged in')
                {
                    if(localStorage.getItem('Access') != null){                    
                        this.router.navigate(['/workbench']);
                        }
                }
                else
                {                    
                    if (data[0]['sso'] == 'true')
                    {
                        this.sso = true
                        localStorage.setItem('sso','true')
                        if ( sessionStorage.getItem('retry_auth') == 'true')
                        {
                            this.router.navigate(['/auth'])
                        }
                    }
                    else
                    {
                        localStorage.setItem('sso','false')
                        this.sso = false
                        if(localStorage.getItem('Access') != null){                    
                            this.router.navigate(['/workbench']);
                            }                
                    }
                }
            })
        }     
    }, err =>{
        this.message = 'Could not login! Please try again later';
    });
    }
    login(){
        this.passwordFormat=/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$/;
        if(this.password == ''){
            alert('Please enter Password');
            return;
        }
        if(!this.passwordFormat.test(String(this.password.trim()))){
               alert("password is invalid");
                return;
              }
        if(this.username && this.password){
            let formData = new FormData();
            formData.append('User', this.username);
            formData.append('Password', this.password);
            this.httpClient.post('/api/validateUser', formData , { responseType : 'json' }).subscribe(data=>{
                if(data[0]['Status']=='Success'){
                    localStorage.setItem('Access' , data[0]['Access']);
                    localStorage.setItem('TeamID', data[0]['TeamID']);
                    this.router.navigate(['/workbench']);
                }else{
                    this.message = 'Invalid username or password';
                    this.errorMessage = true;
                }
            }, err =>{
                this.message = 'Could not login! Please try again later';
            });
        }
    }
    loginsso(){
        let formData = new FormData();
        formData.append('User', "");
        formData.append('Password', "");
        this.httpClient.post('/api/validateUser', formData , { responseType : 'json' }).subscribe(data=>{
            if (data[0]['Status'] == 'redirect'){
                localStorage.setItem('auth_state',data[0]['State']) 
                window.open(data[0]['redirect_url'], "SSO Authentication", "toolbar=1, scrollbars=1, resizable=1, width=" + 800 + ", height=" + 600);               
                this.router.navigate(['/auth']);
            }
        }, err =>{
            this.message = 'Could not login! Please try again later';
        });
    }
    resetPassword(){
        this.errorMessage = false;
        let proceed = true;
        this.passwordFormat=/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$/;
         if(this.loginType=='reset'){
        if(this.oldPassword == ''){
            alert('Please enter the Password');
            return;
        }
        if(!this.passwordFormat.test(String(this.oldPassword.trim()))){
            alert("old password is invalid");
             return;
           }
           if(this.newPassword == ''){
            alert('Please enter the Password');
            return;
           }
           if(!this.passwordFormat.test(String(this.newPassword.trim()))){
            alert("new password is invalid");
             return;
           }
           if(this.re_enterPassword == ''){
            alert('Please enter the Password');
            return;
           }
           if(!this.passwordFormat.test(String(this.re_enterPassword.trim()))){
            alert("re-entered password is invalid");
             return;
           }
        }
        if(this.loginType=='new'){
            if(this.newPassword == ''){
                alert('Please enter the Password');
                return;
               }
               if(!this.passwordFormat.test(String(this.newPassword.trim()))){
                alert("new password is invalid");
                 return;
               }
               if(this.re_enterPassword == ''){
                alert('Please enter the Password');
                return;
               }
               if(!this.passwordFormat.test(String(this.re_enterPassword.trim()))){
                alert("re-entered password is invalid");
                 return;
               }
        }
        proceed = (this.loginType == 'reset'   && !this.oldPassword) ? false : true;
        if(this.username && this.newPassword && proceed){
            if(this.newPassword == this.re_enterPassword){
                let formData = new FormData();
                formData.append('User', this.username);
                if(this.oldPassword){ formData.append('OldPassword', this.oldPassword); }
                formData.append('NewPassword', this.newPassword);
                this.httpClient.put('/api/resetPassword', formData, { responseType : 'json' }).subscribe(data => {
                    if(data[0]['Status']=='Success'){
                        this.loginType = 'login';
                    }else{
                        this.message = 'Incorrect old password';
                        this.errorMessage = true;
                    }
                }, err => {         
                    this.message = 'Could not reset password! Try again later';
                    this.errorMessage = true;
                });
            }else{
                this.message = 'Passwords does not matching!';
                this.errorMessage = true;
            }
        }else{
            this.message = proceed ? 'Please enter a valid password' : 'enter old password';
            this.errorMessage = true;
        }
    }
    validate(){
        this.errorMessage = false;
        if(this.username){
            let formData = new FormData();
            formData.append('User', this.username);
            this.httpClient.post('/api/checkUser', formData, { responseType : 'json' }).subscribe(data => {
                if(data[0]['Status']=='Success'){
                    if(data[0]['Access']=='NormalUser'){
                        this.loginType = 'reset';
                    }else{
                        this.loginType = 'new';
                    }
                }else{
                    this.message = 'User does not exist';
                    this.errorMessage = true;
                }
            }, err=>{
                console.log('Error in httpClient of validate() mehtod');
            });
        }
    }
    verifyUserId(){
        this.loginType = 'verify';
    }
    cancel(){
        this.errorMessage = false;
        this.loginType = 'login';
    }
}