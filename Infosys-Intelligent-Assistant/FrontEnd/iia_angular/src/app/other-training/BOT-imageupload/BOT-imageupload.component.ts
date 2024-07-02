/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import {Component, OnInit, ViewChild,ElementRef} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import { MatTableDataSource, MatSort, MatPaginator,MatDialog,MatDialogRef } from '@angular/material';
import { DataSource } from '@angular/cdk/table';
import { strictEqual } from 'assert';
import { LoaderComponent } from '../../loader/loader.component';
import { ImageViewerConfig, CustomEvent } from 'ngx-image-viewer/src/app/image-viewer/image-viewer-config.model';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs/Subscription';
import { NgbModal, NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { OneShotModalComponent } from '../oneshot-learning/oneshot-modal/oneshot-modal.component';
import { ActivatedRoute } from '@angular/router';
import { AppRoutingModule } from '../../app.routing';
// MDB Angular Pro


@Component({
    selector: 'app-BOT-imageupload',
    templateUrl: './BOT-imageupload.component.html',
    styleUrls: ['./BOT-imageupload.component.css']
})



export class BotImageUploadComponent implements OnInit  {
    @ViewChild('imageFileDetails') fileInput:ElementRef;
    application_imagename:any=[];
    json_data_blob:Blob;
    uploadSuccess: boolean=false;
    config: ImageViewerConfig = { customBtns: [{ name: 'print', icon: 'fa fa-print' }, { name: 'link', icon: 'fa fa-link' }] };
    imageIndexOne: number = 0;
    mandatorydata_Filled:boolean;

    workflowName: string = "";
    taskName: string="";

    constructor(private httpclient: HttpClient,private dialog:MatDialog, private activateRoute:ActivatedRoute ){
        
    }
    
    urls=[];
    previewData=[];
    column_dict={};
    selected_files=[];
    fileBrowser:any=[];
    json_data={};
    reader:any;
    columnsSelected:any=[];
    columnNames:any=[];
    loader: boolean;
    filesSelected:boolean=false;

    ngOnInit() {
        this.workflowName=this.activateRoute.snapshot.paramMap.get("workflowname");
        this.taskName=this.activateRoute.snapshot.paramMap.get("taskname");
        this.fileBrowser=[];
      
        //getting column names dynamically 
        this.httpclient.get('/api/imageAnalysis/getColumnNames').subscribe(data=> {
          if(data['response'] != 'failure'){
              this.columnsSelected=data ['response'];
            // console.log("columnsSelected is ",this.columnsSelected);
            this.columnNames=this.columnsSelected
          }else{
            console.warn('Could not get data from api!');
          }
        }, err=> {
          console.error('Could not get data! ,'+err)
        });

    }

    onSelectFile(event){
      if (event.target.files && event.target.files[0]) {
          var filesAmount = event.target.files.length;
          let exm:string;
          this.fileBrowser.push.apply(this.fileBrowser,this.fileInput.nativeElement.files);
          for (let i = 0; i < this.fileBrowser.length; i++) {
                  var reader = new FileReader();
                  reader.onload = (event:any) => {
                  exm=this.fileBrowser[i].name
                  let rand_numb=Math.floor(100 + Math.random() * 900);
                  let image_name_value=this.workflowName+"_"+this.taskName+"_"+rand_numb;
                  this.column_dict={'url':event.target.result,'image_name':image_name_value,'error_details':'','workflow_name':this.workflowName,'task_name':this.taskName}
                  //initial mandatory fields
                  // this.urls.push({'url':event.target.result,'image_name':'','error_details':'','workflow_name':this.workflowName,'task_name':this.taskName})

                  for(let i=0;i<this.columnNames.length;i++){
                    this.column_dict[this.columnNames[i]]='';
                  }

                  this.urls.push(this.column_dict);
                  // this.urls.push({'url':event.target.result,'image_name':'','app_name':'','sub_appname':'', 'error_details':'','resolution_steps':'','workflow_name':this.workflowName,'task_name':this.taskName}); 
                  this.json_data[exm]='';
                  }
                  this.filesSelected=true;  
                  reader.readAsDataURL(event.target.files[i]);
          }
          this.fileInput.nativeElement.value="";
      }
  }



  changeValue(id: number, property: string, event: any) {
    const editField = event.target.textContent; 
    
  }


  

  removeimage(img_to_remove){
    //   delete this.urls[img_to_remove]
    let index=this.urls.indexOf(img_to_remove)
    // this.fileInput.nativeElement.files[0].value="";
    this.urls.splice(index,1);
    this.fileBrowser.splice(index,1);
    // console.log("value here ",this.fileInput.nativeElement.value);
    
    if(this.fileBrowser.length==0){
      this.filesSelected=false;
      console.log("value at last  here ",this.fileInput.nativeElement.value);
      this.fileInput.nativeElement.value="";//this makes text to No files chosen after final deletion
    }

  }
  
// new implementation for saving and uploading images
save_UploadImages(){
  console.log('in new upload image details...');
  if(this.fileBrowser.length>0){
    this.loader=true;
    const formData = new FormData();
    formData.append('mappedHeaders',JSON.stringify(this.urls));
    // formData.append('mappedHeaders',JSON.stringify(this.urls));
    for (let i =0;i<this.fileBrowser.length;i++){
      formData.append(this.urls[i].image_name.trim(), this.fileBrowser[i]); 
    }
    console.log("new api ",formData);
    this.httpclient.post('/api/imagedetails/save/imagevector', formData,{responseType:'text'})
    .subscribe(data=>{
      console.log("data is ",data)
      if(data == "success") {
        this.loader=false;
        this.uploadSuccess = true;
        this.previewData=this.urls;
        this.urls=[]//clearing after success
        this.filesSelected=false;
        this.ngOnInit();
      }else{
        console.log('Oops!!, No any data received');
        alert('We dont support this type of FIles,please check the format ');
        this.uploadSuccess = false;
      }
      this.loader=false;

    })
  }

  else{
    alert('Please choose the right file..!');
  }


}





  //first implementation with two sepearte API calls which is not used now 
  uploadImageFile(){
        console.log('in upload image details...');
        if (this.fileBrowser.length>0) {
            this.loader=true;
            this.httpclient.post('/api/imagedetails/save', this.urls, {responseType: 'text'})
            .subscribe(data => {
              if(data == "success") {
              console.log("image details saved here");
              const formData = new FormData();
              for (let i =0;i<this.fileBrowser.length;i++){
                formData.append(this.urls[i].image_name.trim(),this.fileBrowser[i],this.fileBrowser[i].name)
              }
              
              this.httpclient.post('/api/createimagevector/save', formData, {responseType: 'text'})
              .subscribe(data => {
                console.log("data is ",data)
                if(data == "success") {
                  this.loader=false;
                  this.uploadSuccess = true;
                  this.urls=[]//clearing after success
                  this.filesSelected=false;
                  this.ngOnInit();
                }else{
                  console.log('Oops!!, No any data received');
                  alert('We dont support this type of FIles,please check the format ');
                  //remove the data inserted into the DB 
                  this.uploadSuccess = false;
                   
    
                }
                this.loader=false;
              });
              }
              else{
                console.log('Oops!!, No any data received');
               
              }
            });
          
        }else{
          alert('Please choose the right file..!');
        }
      }


    
      
      private openDialog(image_name) {
        let index=0;
        let data2Model={};
        for(let url_each of this.urls){
           
          if(url_each.image_name==image_name && url_each.image_name!='' ){
            data2Model=url_each;
            const dialogRef = this.dialog.open(OneShotModalComponent,{height:'400px',width:'400px',data:data2Model});
            dialogRef.afterClosed().subscribe(data=>{
              url_each=data;
              console.log(url_each)
              
            })
            break
          }
          index=index+1;
        }
        if(index==this.urls.length){
            alert("please enter imagename")  
        }
          
      } 


}