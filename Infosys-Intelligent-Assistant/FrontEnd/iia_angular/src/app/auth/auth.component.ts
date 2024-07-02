/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import {  HttpClient } from '@angular/common/http';
import { config } from '../config';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css']
})
export class AuthComponent implements OnInit {

  code:string = ''
  res_state:string = ''
  auth_state:string = ''
  errorMessage : boolean;
  message : string;
  

  constructor( private router: Router, private httpClient: HttpClient) { }

  ngOnInit(): void {

    console.log('Waiting timeout')
    
    setTimeout(() => {
      console.log('Sending Auth to Api')
      let expected_state = localStorage.getItem('auth_state').toString()
      let formData = new FormData();
      if (expected_state != null)
      {
        formData.append('State', expected_state);
      }
      this.httpClient.post('/api/auth', formData , { responseType : 'json' }).subscribe(data=>{
        if(data[0]['Status'] == 'Success')
        {                 
      	 if (expected_state == data[0]['State'] )    
          {           
            sessionStorage.setItem('retry_auth', 'false')
            localStorage.setItem('UserId',data[0]['UserId'])
            localStorage.setItem('Access' , data[0]['Access']);
            localStorage.setItem('TeamID', data[0]['TeamID']);  
            sessionStorage.setItem('Access', data[0]['Access'])       
            this.router.navigate(['/workbench'])
	        }
	      }
        else if (data[0]['Status'] == 'Failure')
        {
          this.errorMessage = true
          this.message = "Invalid Authentication please try again"
          sessionStorage.setItem('retry_auth', 'false')
        }
        else
        {         
          console.log('Status: ' + data[0]['Status'])
          console.log('retry login')
	        sessionStorage.setItem('retry_auth', 'true')
          this.router.navigate(['/login'])
        }
                
      })   
    }, 10000);
    
  }

}
