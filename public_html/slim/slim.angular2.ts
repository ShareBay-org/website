/*
 * Slim v4.3.0 - Image Cropping Made Easy
 * Copyright (c) 2017 Rik Schennink - http://slimimagecropper.com
 */
const SlimLib = require('./slim.commonjs');

// Angular core
import { ViewChild, NgModule, Component, Input, ElementRef, OnInit } from "@angular/core";

@Component({
	selector: 'slim',
	template: '<div #root><ng-content></ng-content></div>'
})

@NgModule({
	declarations: [ Slim ],
	exports: [ Slim ]
})

export class Slim {

	@ViewChild('root')
	element:ElementRef;

	@Input()
	options: Object;

	ngOnInit():any {
		SlimLib.create(this.element.nativeElement, this.options);
	}

};