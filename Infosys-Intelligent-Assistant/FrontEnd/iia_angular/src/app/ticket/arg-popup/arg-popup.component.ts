/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, Input, OnInit, EventEmitter, Output } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { CloudData, CloudOptions } from 'angular-tag-cloud-module';
import { ViewEncapsulation } from '@angular/core';
import { delay } from 'q';
import { RequestOptions } from '@angular/http';
import {LogsComponent} from '../logs/logs.component'
@Component({
  selector: 'app-arg-popup',
  templateUrl: './arg-popup.component.html',
  styleUrls: ['./arg-popup.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class ArgsComponent implements OnInit {
  @Input() dataToTakeAsInput: any;
  argList:any={}
  closeResult: string;
  objectKeys:any;
  script:any;
  scriptStatus:boolean=false;
  argValue:any={}
  message:string;
  type:any;
  argStatus:boolean=false;
  envList:any=['Local']
  selectedEnv:any='Local';
  @Output() emitData = new EventEmitter();
  scriptDetails:string;
  scriptType:string;
  runTypeStatus:boolean;
  logs:any={}
  auditLogs:any=[]
  diagName:string;
  argTypes:any=[]
  ngOnInit() {
    if(this.dataToTakeAsInput['Script']){
      this.script=this.dataToTakeAsInput['Script']
      this.argTypes=this.dataToTakeAsInput['DataTypes']
      let formdata=new FormData()
      formdata.append('Script',this.script)
      this.httpClient.post('/api/getArgumentsFromFile',formdata).subscribe(data=>{
        let temp:any;
        temp=data
        temp.forEach(element => {
          this.argList[element]=this.argTypes[temp.indexOf(element)]
        });
        if (Object.keys(this.argList).length==0){
          this.argStatus=true;
        }
        else if(this.argList.toLowerCase().includes('failure')){
          alert(this.argList)
        } 
      })
      let tempList:any=[]
      this.httpClient.get("/api/getEnvironments").subscribe(data=>{
        tempList=data
        tempList.forEach(element => {
          this.envList.push(element['name'])
        });
      })
      this.runTypeStatus=false;
    }else{
      this.scriptType=this.dataToTakeAsInput['Type']
      this.scriptDetails=this.dataToTakeAsInput['ScriptDetails']
      if(this.scriptType=='diagnostic'){
        this.diagName=this.dataToTakeAsInput['DiagName']
        this.scriptDetails['diag_name']=this.diagName
        this.httpClient.get('/api/getArguments/'+this.scriptType+'/'+this.scriptDetails['diag_name']).subscribe(data=>{
          this.argList=data
          if (Object.keys(this.argList).length==0){
            this.argStatus=true;
          }
          else if(this.argList.toLowerCase().includes('failure')){
            alert(this.argList)
          }
        })
      }else{
        this.httpClient.get('/api/getArguments/'+this.scriptType+'/'+this.scriptDetails['name']).subscribe(data=>{
          this.argList=data
          if (Object.keys(this.argList).length==0){
            this.argStatus=true;
          }
          else if(this.argList.toLowerCase().includes('failure')){
            alert(this.argList)
          }
        })
      }
      this.runTypeStatus=true;
    }
  }
  constructor(private httpClient: HttpClient, private modalService: NgbModal, public  activeModal:  NgbActiveModal) {
  }
  open(content) {
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title', size: "lg" }).result.then((result) => {
      this.closeResult = 'Closed with: ${result}';
    });
  }
  compile(){
    Object.keys(this.argList).forEach(key1 => {
      Object.keys(this.argList).forEach(key2 => {
        if(key1==key2){
          if(!this.argList[key1].toLowerCase().includes('str')){
            this.argValue[key1]==Number(this.argValue[key1])
          }
        }
      });
    });
    let temp:any='';
    if (this.script.length!=0){
      this.scriptStatus=false;
      let formdata=new FormData()
      formdata.append('Script',this.script)
      formdata.append('Args',JSON.stringify(this.argValue))
      this.httpClient.post('/api/compileCode',formdata,{responseType:'text'}).subscribe(data=>{
        temp=data
        if(temp.toLowerCase().includes("failure") || temp.toLowerCase().includes("access denied") || temp.toLowerCase().includes("error") || temp.toLowerCase().includes("exception")){
          this.type = 'warning'; 
          this.message = data; 
          this.scriptStatus=true;
        }else{
          this.type = 'success'; 
          this.message = "Compiled Successfully"; 
          this.scriptStatus=true;
          this.emitData.next(true);
        }
      })
    }
}
invokeResolution(){
  alert("Execution Started!!! Please wait for its completion.")
  let ScriptName:any;
  if(this.scriptDetails['type']=='script'){
    if (Object.keys(this.argValue).length!=0){
      if(this.scriptType=='main'){
        ScriptName=this.scriptDetails["name"]
      }else{
        ScriptName=this.scriptDetails["diag_name"]
      }
      this.logs={}
      let formData = new FormData();
      formData.append('ScriptName', ScriptName);
      formData.append('Environment',this.scriptDetails["environment"])
      formData.append('Type',this.scriptType)
      formData.append('Args',JSON.stringify(this.argValue))
      this.httpClient.post("/api/invokeIopsScripts", formData, {responseType:'text'}).subscribe(data=>{
        this.logs[this.scriptDetails["name"]]=data;
          this.type = 'success'; 
          this.message = "Operation Completed"; 
          this.scriptStatus=true;
        if (!(data.toLowerCase().includes('exception')) && !(data.toLowerCase().includes('err')) && !(data.toLowerCase().includes('error')) && !(data.toLowerCase().includes('access denied'))){
          if(this.scriptType=='main'){
            this.SaveResolutionDetails(this.scriptDetails['type'],ScriptName,'success','Running Script : '+data) 
          }else{
            this.SaveResolutionDetails(this.scriptDetails['type'],ScriptName,'success','Running Diagnostic Script : '+data) 
          }
        }else{
          if(this.scriptType=='main'){
            this.SaveResolutionDetails(this.scriptDetails['type'],ScriptName,'failure','Running Script : '+data) 
          }else{
            this.SaveResolutionDetails(this.scriptDetails['type'],ScriptName,'failure','Running Diagnostic Script : '+data) 
          }
        }
        this.httpClient.get('/api/getAuditLogs/'+this.dataToTakeAsInput["IncidentNumber"]).subscribe(data=>{
          this.auditLogs=data;
          this.auditLogs.reverse()
          this.emitData.next(this.auditLogs);
        })
      })
    }else{
      alert('Provide all Arguments')
    }
  }
}
showLogs(value:any){
  const modalRef = this.modalService.open(LogsComponent, { size: 'lg',backdrop:false});
  let dataPassToChild: any = {};
  dataPassToChild['Logs'] = this.logs;
  (<LogsComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch( (result) => {
      console.log(result);
    });
}
SaveResolutionDetails(type:any,name:any,status:any,logs:any){
  let formdata=new FormData()
  formdata.append('Number',this.dataToTakeAsInput["IncidentNumber"])
  formdata.append('Description',this.dataToTakeAsInput["Description"])
  formdata.append('Type',type)
  formdata.append('Name',name)
  formdata.append('Status',status)
  formdata.append('Logs',logs)
  this.httpClient.post('/api/SaveResolutionDetails',formdata,{responseType:'text'}).subscribe(data=>{
    //console.log(data)
  })
}
  closeAlert(){
    this.scriptStatus=false;
  }
}