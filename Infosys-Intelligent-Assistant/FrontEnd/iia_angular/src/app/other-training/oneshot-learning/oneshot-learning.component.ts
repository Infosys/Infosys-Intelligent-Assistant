/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import {Component, ViewChild,ElementRef,Inject} from '@angular/core';
import { MAT_DIALOG_DATA,MatDialogRef,MatDialog } from '@angular/material/dialog';
import {ChooseImageModalComponent} from './chooseimage-modal/chooseimage-modal.component';



@Component({
  selector: 'app-oneshot-learning',
  templateUrl: './oneshot-learning.component.html',
  styleUrls: ['./oneshot-learning.component.css']
})

export class OneshotLearningComponent{

  uploadSuccess: boolean=false;
    
    constructor(private matdialogref:MatDialog){}

    

    chooseImageDialog(){
      // this.matdialogref.open(ChooseImageModalComponent,{height:'500px',width:'900px'});
      const matdialog =this.matdialogref.open(ChooseImageModalComponent,{height:'500px',width:'900px',data:{'upload':this.uploadSuccess}});
      matdialog.afterClosed().subscribe(result => {
        console.log("the result is ",result)
        console.log('The dialog was closed');
        this.uploadSuccess=result
        // this.uploadSuccess = true;
      });


    }

}