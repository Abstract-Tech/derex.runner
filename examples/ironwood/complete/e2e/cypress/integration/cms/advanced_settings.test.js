describe("advanced settings test", () => {
    const cms_url = Cypress.env("CMS_URL");
    const course_id = Cypress.env("DEMO_COURSE_ID");
    const demo_course = `${cms_url}/course/${course_id}`;
  
    it("allows admin to change sittings ", () => {
      cy.login_CMS(Cypress.env("edx_user"), Cypress.env("edx_password"));
  
      // visit the demo course
      cy.visit(demo_course);
  
      // go to setting then advanced settings
      cy
        .get(".nav-course-settings-advanced > a")
        .wait(1500)
        .click({ force: true });
  
      /* check the input of Allow Anonymous Discussion Posts to Peer if the contains is false */
  
      cy
        .get(
          ":nth-child(3) > .value > .CodeMirror > .CodeMirror-scroll > .CodeMirror-sizer  .CodeMirror-lines  pre .cm-atom"
        )
        .contains("false");
      /* check the input of Course Visibility In Catalog if the contains is both */
      cy
        .get(
          ":nth-child(24) > .value > .CodeMirror > .CodeMirror-scroll > .CodeMirror-sizer .CodeMirror-lines pre .cm-string"
        )
        .contains("both");
    });
  });