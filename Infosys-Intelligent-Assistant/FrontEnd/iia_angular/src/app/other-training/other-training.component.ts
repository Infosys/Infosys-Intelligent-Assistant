/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import {Component, OnInit} from '@angular/core';
import {HttpClient} from '@angular/common/http';

@Component ({
    selector : 'app-other-training',
    templateUrl : './other-training.component.html',
    styleUrls : ['./other-training.component.css']
})

export class OtherTrainingComponent{


    haveTrainingDataState: boolean;

    constructor(private httpclient: HttpClient) {
        httpclient.get('/api/getTrainedTicketsCount', {responseType:'text'}).subscribe(data=> {
            if(Number(data) > 0) this.haveTrainingDataState= true;
            else this.haveTrainingDataState= false;
        });
    }
}