;;; facet.el --- work on a facet
;; Version: 0.0.0
;; Author: dandavison7@gmail.com
;; Keywords: project, task
;; URL: https://github.com/dandavison/facet

(defvar facet-current-project nil)

(defvar facet-directory nil)

;;;###autoload
(defun facet (arg)
  (interactive "P")
  (call-interactively
   (if arg 'facet-workon 'facet-goto-project-directory)))

;;;###autoload
(defun facet-workon (project-name)
  "Set current project."
  (interactive
   (list
    (completing-read
     "Project name: " (directory-files facet-directory nil "^[^.]"))))
  (setq facet-current-project project-name))

;;;###autoload
(defun facet-goto-project-directory ()
  "Open dired buffer on project directory"
  (interactive)
  (dired (expand-file-name facet-current-project facet-directory)))

(provide 'facet)
;;; facet.el ends here
