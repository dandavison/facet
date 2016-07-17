;;; facet.el --- work on a facet
;; Version: 0.0.0
;; Author: dandavison7@gmail.com
;; Keywords: project, task
;; URL: https://github.com/dandavison/facet

(defvar facet-directory (expand-file-name "~/.facet/"))

;;;###autoload
(defun facet (arg)
  (interactive "P")
  (call-interactively
   (if arg 'facet-workon 'facet-cd)))

;;;###autoload
(defun facet-workon (facet-name)
  "Set current facet."
  (interactive
   (list
    (completing-read
     "Facet name: " (facet-list))))
  (facet-write-state 'facet facet-name))

;;;###autoload
(defun facet-workon-helm ()
  "Set current facet."
  (interactive)
  (helm
   :sources
   `((name . "Facets")
     (candidates . ,(facet-list))
     (action . facet-workon))))

;;;###autoload
(defun facet-cd ()
  "Open dired buffer on facet directory"
  (interactive)
  (dired (expand-file-name (facet-current-facet) (facet-facets-directory))))

(defun facet-list ()
  (directory-files (facet-facets-directory) nil "^[^.]"))

(defun facet-current-facet ()
  (cdr (assoc 'facet (facet-read-state))))

(defun facet-facets-directory ()
  (expand-file-name "facets" facet-directory))

(defun facet-state-file ()
  (expand-file-name "state.json" facet-directory))

(defun facet-read-state ()
  (json-read-file (facet-state-file)))

(defun facet-write-state (key value)
  (write-region
   (json-encode
    (append
     (assq-delete-all key (facet-read-state))
     `((,key . ,value))))
   nil (facet-state-file)))


(provide 'facet)
;;; facet.el ends here
