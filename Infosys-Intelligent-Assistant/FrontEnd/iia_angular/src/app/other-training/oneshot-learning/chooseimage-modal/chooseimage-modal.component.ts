/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import {Component, OnInit, ViewChild,ElementRef} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import { MatTableDataSource, MatSort, MatPaginator,MatDialog,MatDialogRef } from '@angular/material';
import { DataSource } from '@angular/cdk/table';
import { strictEqual } from 'assert';
import { LoaderComponent } from '../../../loader/loader.component';
import { ImageViewerConfig, CustomEvent } from 'ngx-image-viewer'
import { Router } from '@angular/router';
import { Subscription } from 'rxjs/Subscription';
import { NgbModal, NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { OneShotModalComponent } from '../oneshot-modal/oneshot-modal.component';




@Component({
    selector: 'app-chooseimage-modal',
    templateUrl: './chooseimage-modal.component.html',
    styleUrls: ['./chooseimage-modal.component.css']
})



export class ChooseImageModalComponent implements OnInit  {
    @ViewChild('imageFileDetails') fileInput:ElementRef;
    application_imagename:any=[];
    json_data_blob:Blob;
    uploadSuccess: boolean=false;
    config: ImageViewerConfig = { customBtns: [{ name: 'print', icon: 'fa fa-print' }, { name: 'link', icon: 'fa fa-link' }] };
    imageIndexOne: number = 0;
    mandatorydata_Filled:boolean;

    constructor(private httpclient: HttpClient,private dialog:MatDialog,public dialogRef:MatDialogRef<ChooseImageModalComponent> ){
        
      }
  

    urls=[];
	selected_files=[];
	fileBrowser:any=[];
    json_data={};
    
    loader: boolean;
    filesSelected:boolean=false;

    ngOnInit() {
      this.fileBrowser=[];

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
                  
                  this.urls.push({'url':event.target.result,'image_name':'','app_name':'','sub_appname':'', 'error_details':'','resolution_steps':''}); 
                  //this.selected_files.push(fileBrowser.files[i]);
                  this.json_data[exm]='';
                  }
                  this.filesSelected=true;  
                  console.log("here am",event.target.files[i])
                  reader.readAsDataURL(event.target.files[i]);
          }
          this.fileInput.nativeElement.value="";
      }
  }



    zoom(){ 
      
    let imageId = document.getElementById('view');
    if(imageId.style.width == "400px"){
    imageId.style.width = "300px";
    imageId.style.height = "300px";
    }else{
     imageId.style.width = "400px";
    imageId.style.height = "400px";
    }
  }

  removeimage(img_to_remove){
    //   delete this.urls[img_to_remove]
    let index=this.urls.indexOf(img_to_remove)
    this.urls.splice(index,1);
    this.fileBrowser.splice(index,1);

    if(this.fileBrowser.length==0){
      this.filesSelected=false;
      console.log("value at last  here ",this.fileInput.nativeElement.value);
      this.fileInput.nativeElement.value="";//this makes text to No files chosen after final deletion
    }

  }
  
  
  uploadImageFile(){
        if (this.fileBrowser.length>0) {
          
          for (let i =0;i<this.fileBrowser.length;i++){
            if((this.urls[i]['app_name']==''||this.urls[i]['sub_appname']=='')){
              this.mandatorydata_Filled=false;
              alert("please fill mandatory fields for the image "+ this.urls[i]['image_name'])

            }
            else{
              this.mandatorydata_Filled=true;
            }
          }

          if(this.mandatorydata_Filled==true){
            // code to remove auto generated  url now we r doing this in backend itself

            this.loader=true;
            this.httpclient.post('/api/imagedetails/save', this.urls, {responseType: 'text'})
            .subscribe(data => {
              if(data == "success") {
              }else{
                console.log('Oops!!, No any data received');
               
              }
            });
          

         
          
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
              // i have to reload the page with out images and just show success text in front end 
            this.dialogRef.close(this.uploadSuccess)
            }else{
              console.log('Oops!!, No any data received');
              alert('We dont support this type of FIles,please check the format ')
              this.uploadSuccess = false;
               

            }
            this.loader=false;
          });

         }
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