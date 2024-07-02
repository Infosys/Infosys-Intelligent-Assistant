/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http'
import {FormControl, Validators} from '@angular/forms';
@Component({
    selector : 'app-itsm-usermap',
    templateUrl : './itsm-user-map.component.html',
    styleUrls : ['./itsm-user-map.component.css']
})
export class ITSMUserMapComponent implements OnInit {
    customerId : number = 1;
    email : string;
    name : string;
    password :  string;
    teams : any = [];
    // usersLst : any = [];
    teamID : string;
    message : string;
    color : string;
    showMessage : boolean;
    selectedTeam : string;
    selectedName : string;
    itsmName : string;
    resourceLst : any = [];
    mappedLst : any = [];
    constructor(private httpClient: HttpClient) {}
    ngOnInit() {
        this.httpClient.get('/api/getTeamNameWithId/' + this.customerId).subscribe(data => {
            if (Object.keys(data).length > 0) {
                this.teams = data; 
                this.selectedTeam = this.teams[0].TeamName;
                this.getMappedInfo();
                this.teamIdChanged();
            }
        }, err => {
            console.log('Could not get team names with id! please try again later');
        });
    }
    getMappedInfo(){
        this.httpClient.post('/api/itsmUsers/'+this.customerId+'/get',null,{responseType:'json'}).subscribe(data => {
            this.mappedLst = data;
        },err => {
            console.log('Could not get mapped info! Please try again later');
        });
    }
    submit(){
        let mappedDoc = {};
        this.color = 'red';
        var nameFormat = /^[a-zA-Z0-9 _.-]*$/;
        //check empty value
        if(this.itsmName == undefined || this.itsmName.trim()== ''){
            alert("Please Enter ITSM User name");
            return;
        }
        if(!nameFormat.test(String(this.itsmName).toLowerCase())){
            alert("ITSM User name is invalid");      
            return;      
        }
        if(this.customerId && this.selectedTeam && this.selectedName && this.itsmName){
            mappedDoc['CustomerID'] = this.customerId;
            mappedDoc['teamName'] = this.selectedTeam;
            mappedDoc['user'] = this.selectedName;
            mappedDoc['mapped_user'] = this.itsmName;
            this.httpClient.post('/api/itsmUsers/'+this.customerId+'/post',mappedDoc,{responseType:'text'}).subscribe(msg => {
                this.showMessage = true;
                if(msg == 'success'){
                    this.color = 'green';
                    this.message = 'Saved Successfully!';
                    this.selectedName = '';
                    this.itsmName = '';
                    this.getMappedInfo();
                }else{
                    this.message = 'Could not save! Try again';
                }
            }, err =>{
                console.log('Could not save mapped details! Please try again later');
            });
        }else{
            this.showMessage = true;
            this.message = 'Fill all fields';
        }
    }
    removeUser(mappedDoc){
        delete mappedDoc._id
        this.httpClient.post('/api/itsmUsers/'+this.customerId+'/delete',mappedDoc,{responseType:'text'}).subscribe(msg => {
            if(msg == 'success'){
                this.color = 'green';
                this.message = 'Deleted Successfully!';
                this.selectedName = '';
                this.itsmName = '';
                this.getMappedInfo();
            }else{
                this.color = 'red';
                this.message = 'Could not delete! Try again';
            }
        }, err =>{
            console.log('Could not delete mapped details! Please try again later');
        });
    }
    emailFormControl = new FormControl('', [
        Validators.required,
        Validators.email,
    ]);
    teamIdChanged(){
        this.httpClient.get('/api/getResourceDetails/'+this.customerId+'/'+this.selectedTeam).subscribe(data => {
            if(Object.keys(data).length > 0){
                this.showMessage =false;
                this.resourceLst = data;  
                this.getMappedInfo();
            }else{
                this.color = 'red';
                this.message = 'No resource available for selected team! choose another team';
                this.showMessage = true;
            }
        },err =>{
            console.log('Could not get resource details! Please try again later')
        });
    }
}