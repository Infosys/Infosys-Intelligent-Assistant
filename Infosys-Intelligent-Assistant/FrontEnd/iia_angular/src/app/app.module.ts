/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { RouterModule } from '@angular/router';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import { AppRoutingModule } from './app.routing';
import { ComponentsModule } from './components/components.module';
import { AppComponent } from './app.component';
import {LoadingComponent} from './loading/loading.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { AngularMultiSelectModule } from 'angular2-multiselect-dropdown/angular2-multiselect-dropdown';
import { InputOutputComponent } from './training/input-output/input-output.component';
import { TrainingComponent } from './training/training.component';
import { AlgorithmFilterComponent } from './training/algorithm-filter/algorithm-filter.component';
import { AlgorithmInformationComponent } from './training/algorithm-information/algorithm-information.component';
import { UserPreferenceComponent } from './user-preference/user-preference.component';
import { ResourcePlanningComponent } from './resource-planning/resource-planning.component';
import { ResourceDetailsComponent } from './resource-planning/resource-details/resource-details.component';
import { ApplicationDetailsComponent } from './resource-planning/application-details/application-details.component';
import { RoasterDetailsComponent } from './resource-planning/roaster-details/roaster-details.component';
import { ShiftDetailsComponent } from './resource-planning/roaster-details/shift-details/shift-details.component';
import { PredictComponent } from './predict/predict.component';
import { TicketComponent } from './ticket/ticket.component';
import { RelatedTicketsComponent } from './ticket/related-tickets/related-tickets.component';
import { MatNativeDateModule } from '@angular/material';
import { MatChipsModule } from '@angular/material/chips'
import { AdminLayoutComponent } from './layouts/admin-layout/admin-layout.component';
import { MatTooltipModule } from '@angular/material';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatCheckboxModule } from '@angular/material/checkbox'
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { TuningOptionComponent } from './training/tuning-option/tuning-option.component';
import { ChartsModule } from 'ng2-charts';
import { Chart } from 'chart.js';
import { TagCloudModule } from 'angular-tag-cloud-module';
import { TagInputModule } from 'ngx-chips';
import { NgbModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { LoaderComponent } from './loader/loader.component';
import { PopupModelComponent } from './popup-model/popup-model.component';
import { OpenTicketsComponent } from './ticket/open-tickets/open-tickets.component';
import { WhitelistedWordsComponent } from './training/tuning-option/whitelisted-words/whitelisted-words.component';
import { ValidationMessageComponent } from './resource-planning/validation-message/validation-message.component';
import { LoginComponent } from './login-page/login-page.component';
// import { FlexModule } from '@angular/flex-layout';
import { ScriptsPopupComponent } from './ticket/scripts-popup/scripts-popup.component'
import { LogsComponent } from './ticket/logs/logs.component'
import { ArgsComponent } from './ticket/arg-popup/arg-popup.component'
import { DiagComponent } from './ticket/diag-popup/diag-popup.component'
import { CreateScriptComponent } from './admin/create-script/create-script.component'
import { MatAutocompleteSelectedEvent, MatChipInputEvent, MatAutocomplete, MatChipInput, MatAutocompleteModule } from '@angular/material';
import {
  MatButtonModule,
  MatInputModule,
  MatRippleModule,
  MatSliderModule,
  MatRadioModule
} from '@angular/material';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
// import { CodemirrorModule } from '@ctrl/ngx-codemirror';
import { CodemirrorModule } from 'lib/public_api';
import {
  MatSortModule
} from '@angular/material';
import { MatTableModule, MatPaginatorModule } from '@angular/material';
import { MatSidenavModule } from '@angular/material/sidenav';
import { AnnotationModalComponent } from './ticket/modal-annotation/modal-annotation.component';
import { ImagePreviewerComponent } from './ticket/image-previewer/image-previewer.component';
import { ImageViewerModule } from 'ngx-image-viewer';
import {BotImageUploadComponent} from './other-training/BOT-imageupload/BOT-imageupload.component';
import {OneShotModalComponent} from './other-training/oneshot-learning/oneshot-modal/oneshot-modal.component';
import { ImageOneShotModalComponent } from './ticket/related-tickets/imageoneshot-modal/imageoneshot-modal.component';
import { OrchestratorArgsPopupComponent } from './ticket/orchestrator-args-popup/orchestrator-args-popup.component';
import { CreateRPAComponent } from './admin/create-rpa/create-rpa.component';
import { RpaPopupComponent } from './ticket/rpa-popup/rpa-popup.component';
import { RpaDiagPopupComponent } from './ticket/rpa-diag-popup/rpa-diag-popup.component';
import { AuthComponent } from './auth/auth.component';
import { DatePipe } from '@angular/common';
import { WarningPopupComponent } from './training/warning-popup/warning-popup.component';
@NgModule({
  imports: [
    NgbModule,
    AngularMultiSelectModule,
    MatTabsModule,
    TagInputModule,
    TagCloudModule,
    ChartsModule,
    BrowserAnimationsModule,
    MatSortModule,
    MatTableModule,
    MatButtonModule,
    MatPaginatorModule,
    MatInputModule,
    MatRippleModule,
    MatTooltipModule,
    MatCheckboxModule,
    MatSliderModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    HttpModule,
    ComponentsModule,
    RouterModule,
    AppRoutingModule,
    MatTooltipModule,
    MatIconModule,
    MatSelectModule,
    MatTabsModule,
    MatExpansionModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatCheckboxModule,
    MatChipsModule,
    MatAutocompleteModule,
    MatChipsModule,
    MatSliderModule,
    MatSlideToggleModule,
    CodemirrorModule,
    MatSidenavModule,
    ImageViewerModule,
    MatRadioModule,
  ],
  declarations: [
    AppComponent,
    AdminLayoutComponent,
    TuningOptionComponent,
    RelatedTicketsComponent,
    PopupModelComponent,
    OpenTicketsComponent,
    WhitelistedWordsComponent,
    ValidationMessageComponent,
    LoginComponent,
    AuthComponent,
    ScriptsPopupComponent,
    LogsComponent,
    CreateScriptComponent,
    ArgsComponent,
    DiagComponent,
    AnnotationModalComponent,
    ImagePreviewerComponent,
    BotImageUploadComponent,
    ImageOneShotModalComponent,
    OneShotModalComponent,
    OrchestratorArgsPopupComponent,
    CreateRPAComponent,
    RpaPopupComponent,
    RpaDiagPopupComponent,
    WarningPopupComponent,
    LoadingComponent
  ],
  providers: [DatePipe],
  bootstrap: [AppComponent],
  entryComponents: [TuningOptionComponent, RelatedTicketsComponent, PopupModelComponent, OpenTicketsComponent, WhitelistedWordsComponent, ValidationMessageComponent, ScriptsPopupComponent, LogsComponent, CreateScriptComponent, ArgsComponent, DiagComponent, AnnotationModalComponent, ImagePreviewerComponent, ImagePreviewerComponent,ImageOneShotModalComponent,OneShotModalComponent,OrchestratorArgsPopupComponent, CreateRPAComponent,  RpaPopupComponent,
    RpaDiagPopupComponent,WarningPopupComponent,LoadingComponent]
})
export class AppModule { }
