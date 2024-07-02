/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http'
import { FormControl, Validators } from '@angular/forms';
interface User {
    id?: number;
    UserName: string;
    UserID: string;
    Team: string;
    Role: string;
}
@Component({
    selector: 'app-add-user',
    templateUrl: './add-user.component.html',
    styleUrls: ['./add-user.component.css']
})
export class AddUserComponent implements OnInit {
    customerId: number = 1;
    email: string;
    name: string;
    password: string;
    teams: any = [];
    usersLst: User[] = [];
    teamID: string;
    message: string;
    color: string;
    showMessage: boolean;
    selectedTeam: string;
    selectedRole: string;
    collectionSize: number;
    pageSize: number = 5;
    page: number = 1;
    showTable: boolean = true;
    userFormat: any;
    emailFormat: any;
    constructor(private httpClient: HttpClient) { }
    ngOnInit() {
        this.httpClient.get('/api/getTeamNameWithId/' + this.customerId).subscribe(data => {
            if (Object.keys(data).length > 0) {
                this.teams = data;
            }
        }, err => {
            console.log('Could not get team names with id! please try again later');
        });
        this.loadUsers();
    }
    get users(): User[] {
        return this.usersLst
            .map((user, i) => ({ id: i + 1, ...user }))
            .slice((this.page - 1) * this.pageSize, (this.page - 1) * this.pageSize + this.pageSize);
    }
    loadUsers() {
        this.httpClient.get('/api/getUsers').subscribe(data => {
            if (data != 'failure') {
                let tempLst: any = data;
                this.usersLst = tempLst;
                this.collectionSize = this.usersLst.length;
                this.showTable = true;
            } else {
                this.showTable = false;
                console.log('failure response from backend');
            }
        }, err => {
            console.log('Could not get users! please try again later');
        });
    }
    submit() {
        this.color = 'red';
        this.showMessage = false;
        this.emailFormat = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        this.userFormat = /^[a-zA-Z0-9 _.-]*$/;
        this.email = this.email.trim();
        if (!this.userFormat.test(String(this.name.trim().toLowerCase()))) {
            alert("name is invalid")
            return;
        }
        if (this.email.trim() === "") {
            alert("Email Id cannot be empty")
            return;
        }
        if (!this.emailFormat.test(String(this.email.trim().toLowerCase()))) {
            alert("Email ID is invalid")
            return;
        }
        if (this.email && this.teamID && this.selectedRole && this.name) {
            let formData = new FormData();
            formData.append('UserName', this.name);
            formData.append('UserID', this.email);
            formData.append('TeamID', this.teamID);
            formData.append('Role', this.selectedRole);
            this.httpClient.post('/api/addUser', formData, { responseType: 'text' }).subscribe(data => {
                if (data == 'Success') {
                    this.color = 'green';
                    this.message = 'User has been added succesfully!';
                    this.selectedTeam = '';
                    this.selectedRole = '';
                    this.email = '';
                    this.name = '';
                    this.loadUsers();
                } else {
                    this.message = 'Failed to add new user!';
                }
                this.showMessage = true;
            }, err => {
                this.message = 'Could not add new user, try again later';
                this.showMessage = true;
            });
        } else {
            this.message = '*Please fill all the required fields';
            this.showMessage = true;
        }
    }
    removeUser(userId) {
        if (confirm('Are you sure you want to delete this user?')) {
            this.httpClient.delete('/api/deleteUser/' + userId, { responseType: 'text' }).subscribe(data => {
                this.loadUsers();
            }, err => {
                console.log('Could not delete user! please try again later');
            });
        }
    }
    emailFormControl = new FormControl('', [
        Validators.required,
        Validators.email,
    ]);
}