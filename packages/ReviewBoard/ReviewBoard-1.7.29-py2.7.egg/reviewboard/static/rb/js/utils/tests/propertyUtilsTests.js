describe('propertyUtils', function() {
    var model;

    beforeEach(function() {
        model = new Backbone.Model();
    });

    describe('$.fn.bindProperty', function() {
        var $el;

        beforeEach(function() {
            $el = $("<input type='checkbox'/>").appendTo(document.body);
        });

        afterEach(function() {
            $el.remove();
        });

        describe("Initial property values", function() {
            it("Setting element's property from model property's", function() {
                model.set('mybool', true);
                $el.bindProperty('checked', model, 'mybool');
                expect($el.prop('checked')).toBe(true);
            });

            it("Setting element's property form model property's with " +
               "inverse=true",
               function() {
                model.set('mybool', false);
                $el.bindProperty('checked', model, 'mybool', {
                    inverse: true
                });
                expect($el.prop('checked')).toBe(true);
                expect(model.get('mybool')).toBe(false);
            });

            it('No element changes with modelToElement=false', function() {
                model.set('mybool', true);
                $el.bindProperty('checked', model, 'mybool', {
                    modelToElement: false
                });

                expect($el.prop('checked')).toBe(false);
            });
        });

        describe("Model property changes", function() {
            it("Setting element's property", function() {
                model.set('mybool', false);
                $el.bindProperty('checked', model, 'mybool');
                expect($el.prop('checked')).toBe(false);

                model.set('mybool', true);
                expect($el.prop('checked')).toBe(true);
            });

            it("Setting element's property with inverse=true", function() {
                model.set('mybool', false);
                $el.bindProperty('checked', model, 'mybool', {
                    inverse: true
                });
                expect($el.prop('checked')).toBe(true);

                model.set('mybool', true);
                expect($el.prop('checked')).toBe(false);
                expect(model.get('mybool')).toBe(true);
            });

            it('No element changes with modelToElement=false', function() {
                model.set('mybool', false);
                $el.bindProperty('checked', model, 'mybool', {
                    modelToElement: false
                });

                model.set('mybool', true);
                expect($el.prop('checked')).toBe(false);
            });
        });

        describe("Element property changes", function() {
            it("Setting model's property", function() {
                model.set('mybool', false);
                $el.bindProperty('checked', model, 'mybool');

                $el.click();
                expect($el.prop('checked')).toBe(true);
                expect(model.get('mybool')).toBe(true);
            });

            it("Setting model's property with inverse=true", function() {
                model.set('mybool', false);
                $el.bindProperty('checked', model, 'mybool', {
                    inverse: true
                });

                $el.prop('checked', false);
                $el.click();

                expect($el.prop('checked')).toBe(true);
                expect(model.get('mybool')).toBe(false);
            });

            it("No model changes with elementToModel=false", function() {
                model.set('mybool', false);
                $el.bindProperty('checked', model, 'mybool', {
                    elementToModel: false
                });

                $el.click();
                expect($el.prop('checked')).toBe(true);
                expect(model.get('mybool')).toBe(false);
            });
        });
    });

    describe('$.fn.bindVisibility', function() {
        var $el;

        beforeEach(function() {
            $el = $('<div/>').appendTo(document.body);
        });

        afterEach(function() {
            $el.remove();
        });

        describe('Showing elements', function() {
            it('When property is initially true', function() {
                $el.hide();

                model.set('mybool', true);
                $el.bindVisibility(model, 'mybool');
                expect($el.is(':visible')).toBe(true);
            });

            it('When property is initially false with inverse=true',
               function() {
                $el.hide();

                model.set('mybool', false);
                $el.bindVisibility(model, 'mybool', {
                    inverse: true
                });
                expect($el.is(':visible')).toBe(true);
            });

            it('When property is changed to true', function() {
                expect($el.is(':visible')).toBe(true);

                model.set('mybool', false);
                $el.bindVisibility(model, 'mybool');
                model.set('mybool', true);
                expect($el.is(':visible')).toBe(true);
            });

            it('When property is changed to false with inverse=true',
               function() {
                $el.hide();

                model.set('mybool', true);
                $el.bindVisibility(model, 'mybool', {
                    inverse: true
                });
                model.set('mybool', false);
                expect($el.is(':visible')).toBe(true);
            });
        });

        describe('Hiding elements', function() {
            it('When property is initially false', function() {
                expect($el.is(':visible')).toBe(true);

                model.set('mybool', false);
                $el.bindVisibility(model, 'mybool');
                expect($el.is(':visible')).toBe(false);
            });

            it('When property is initially true with inverse=true',
               function() {
                expect($el.is(':visible')).toBe(true);

                model.set('mybool', true);
                $el.bindVisibility(model, 'mybool', {
                    inverse: true
                });
                expect($el.is(':visible')).toBe(false);
            });

            it('When property is changed to false', function() {
                $el.hide();

                model.set('mybool', true);
                $el.bindVisibility(model, 'mybool');
                model.set('mybool', false);
                expect($el.is(':visible')).toBe(false);
            });

            it('When property is changed to true with inverse=true',
               function() {
                expect($el.is(':visible')).toBe(true);

                model.set('mybool', false);
                $el.bindVisibility(model, 'mybool', {
                    inverse: true
                });
                model.set('mybool', true);
                expect($el.is(':visible')).toBe(false);
            });
        });
    });
});
