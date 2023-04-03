/*
 * Slim v4.3.0 - Image Cropping Made Easy
 * Copyright (c) 2017 Rik Schennink - http://slimimagecropper.com
 */
// Necessary React Modules
import React from 'react';
import ReactDOM from 'react-dom';

// Slim (place slim CSS and module js file in same folder as this file)
import Slim from './slim.module.js';
import './slim.min.css';

// React Component
export default React.createClass({

	componentDidMount() {
		this.instance = Slim ? Slim.create(ReactDOM.findDOMNode(this), this.props) : null;
	},

	render() {
		return <div className="slim">{ this.props.children }</div>
	}

});