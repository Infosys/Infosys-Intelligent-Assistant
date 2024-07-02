/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { FormBuilder, FormControl, FormArray, FormGroup, Validators } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { ResponseType } from '@angular/http';
import { text, template } from '@angular/core/src/render3';
import {COMMA, ENTER} from '@angular/cdk/keycodes';
import {Component, ElementRef, ViewChild,OnInit, Injectable} from '@angular/core';
import {MatAutocompleteSelectedEvent, MatChipInputEvent,MatAutocomplete} from '@angular/material';
import {Observable} from 'rxjs';
import {map, startWith} from 'rxjs/operators';
import {coerceNumberProperty} from '@angular/cdk/coercion'
import {MatTableDataSource,MatPaginator,MatSort,MatPaginatorModule,MatTableModule} from '@angular/material';
import {CreateScriptComponent} from '../create-script/create-script.component'
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { forEach } from '@angular/router/src/utils/collection';
export interface UserData {
  Selected:any;
  environment: string;
  username:string;
  password:string;
  ping:string;
  status:string;
}
@Component({
  selector: 'app-script-run',
  templateUrl: './script-run.component.html',
  styleUrls: ['./script-run.component.css'],
})
export class ScriptRunComponent implements OnInit {
  displayedColumns: string[] = ['Selected','environment','username','password','ping'];
  dataSource: MatTableDataSource<UserData>;
  message:string;
  saveSuccess:boolean=false;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  selectedAll: any;
  updation:boolean;
  addition:boolean=true;
  removal:boolean;
  visible = true;
  selectable = true;
  removable = true;
  addOnBlur = true;
  separatorKeysCodes: number[] = [ENTER, COMMA];
  keywordCtrl = new FormControl();
  filteredKeywords: Observable<string[]>;
  deploymentStatus:boolean;
  scriptName:string="";
  args:boolean;
  invert = false;
  showTicks = false;
  thumbLabel = false;
  value = 0;
  vertical = false;
  argumentCtrl = new FormControl();
  filteredArguments: Observable<string[]>;
  public envInfo:UserData[]=[];
  scripts=[];
  operation:any;
  tempList:any
  closeResult:any;
  scriptsList:any=[]
  accessStatus:boolean;
  accessList:any[] = [];
  scriptDropdown=[]
  constructor(private httpClient: HttpClient, private modalService: NgbModal) {
  }
    ngOnInit(){
      this.envsLoad();
      // this.getScriptNames()
    }
    applyFilter(filterValue: string) {
      this.dataSource.filter = filterValue.trim().toLowerCase();
      if (this.dataSource.paginator) {
        this.dataSource.paginator.firstPage();
      }
    }
    envsLoad(){
      // this.accessList=[]
      this.envInfo=[]
      this.httpClient.get("/api/getEnvironments").subscribe(data=>{
        this.tempList=[]
        this.tempList=data
        this.tempList.forEach(element => {
          this.envInfo.push({Selected:false,environment:element["name"],username:element["username"],password:element["password"],ping:'',status:'Success'})
        });
        // const users =  Array.from({length: this.scriptsInfo.length}, (_, k) => this.createNewUser(k))
          // Assign the data to the data source for the table to render
          this.dataSource = new MatTableDataSource(this.envInfo)
          this.dataSource.paginator = this.paginator;
          this.dataSource.sort = this.sort;
      })
    }
    private selectAll() {
      this.envInfo.forEach((item, index) => {
        item.Selected = this.selectedAll;
      });
    }
    private checkIfAllSelected() {
      this.selectedAll = this.envInfo.every(function(item:any) {
          return item.Selected == true;
      });
    }
    save(){
      let envList=[]
      let count=0
      this.dataSource.data.forEach(element => {
        if(element.Selected){
          if(element.environment.length==0){
            alert('Environment name cannot be empty')
            count=+1
          }else if(element.username.length==0){
            alert('Username cannot be empty')
            count=+1
          }else if(element.password.length==0){
            alert('Password cannot be empty')
            count=+1
          }else{
            envList.push(element)
          }
        }
      });
      if(envList.length==0 && count==0){
        alert("Select atleast one")
      }else if(envList.length!=0 && count==0){
        let formdata=new FormData();
        formdata.append('Environments',JSON.stringify(envList))
        this.httpClient.post('/api/SaveEnvironments',formdata,{responseType:'text'}).subscribe(data=>{
          alert(data)
          this.envsLoad()
        })
      }
    }
    Remove(){
      this.saveSuccess=false;
      let envNames=[]
      this.dataSource.data.forEach(element => {
        if(element.Selected) {
          envNames.push(element['environment']);
        }
      })
      if (envNames.length==0){
        alert("Select atleast one")
      }else{
        let formData=new FormData()
        formData.append('Environments', envNames.join(','));
        this.httpClient.post('/api/deleteEnvironments',formData,{responseType:'text'}).subscribe(data=>{
          alert(data)
          this.envsLoad()
        })
      }
    }
    addElement() {
      this.saveSuccess=false;
      // this.getScriptNames()
      this.envInfo.push({Selected:false,environment:'',username:'',password:'',ping:'',status:'Failure'})
      this.dataSource = new MatTableDataSource(this.envInfo);
    }
    ping(env_details:any){
      if(env_details.environment.length==0){
        alert('Environment name cannot be empty')
      }else if(env_details.username.length==0){
        alert('Username cannot be empty')
      }else if(env_details.password.length==0){
        alert('Password cannot be empty')
      }else{
        let formdata=new FormData();
        formdata.append('Environments',JSON.stringify(env_details))
        this.httpClient.post('/api/ping',formdata,{responseType:'text'}).subscribe(data=>{
          if(!(data.includes('Access denied')) && (!(data.toLowerCase().includes('error')))){
            this.envInfo.forEach(element => {
              if(element==env_details){
                element.status="Success"
              }
            });
            this.dataSource = new MatTableDataSource(this.envInfo);
          }
          else{
            alert('Failure: Please check your connection details')
          }
        })
      }
    }
}