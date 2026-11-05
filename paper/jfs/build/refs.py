r"""Write the JFS reference list into manuscript.tex.

    python -I refs.py <project dir>

Order: first citation, read from manuscript.aux (\citation lines are written
in the order the citations occur, and table- or legend-only references were
placed at the first citation of their table or figure by build_jfs.py).

Style: JFS Information for Authors (June 2025): Vancouver/ICMJE, NLM
journal abbreviations (ISO 4 without full stops where the NLM Catalog has
no entry), six authors then "et al.", DOI at the end. Every entry was
checked against Crossref/DataCite metadata on 6 Nov 2026.
"""
import re
import sys
from pathlib import Path


def doi(d):
    return r"doi: \href{https://doi.org/%s}{%s}" % (d, d.replace("_", r"\_"))


R = {
 "babbar": r"Babbar D, Jain A, Sharma A, Banerjee D. Forgery detection in Aadhaar-based KYC using deep learning. In: Proceedings of the 2024 16th International Conference on Machine Learning and Computing (ICMLC 2024); Shenzhen, China. New York, NY: ACM; 2024. p. 244--50. " + doi("10.1145/3651671.3651691") + ".",
 "vgg": r"Simonyan K, Zisserman A. Very deep convolutional networks for large-scale image recognition. In: Proceedings of the 3rd International Conference on Learning Representations (ICLR 2015); 2015 May 7--9; San Diego, CA. " + doi("10.48550/arXiv.1409.1556") + ".",
 "uidai-scheme": r"Unique Identification Authority of India. A UID numbering scheme. 2010. \url{http://web.archive.org/web/20100704211109/www.uidai.gov.in/documents/A_UID_Numbering_Scheme.pdf}. Accessed 28 Oct 2026.",
 "verhoeff": r"Verhoeff J. Error detecting decimal codes [dissertation]. Amsterdam, the Netherlands: Mathematical Centre; 1969. (Mathematical Centre Tracts; vol. 29).",
 "itd-pan": r"Income Tax Department, Government of India. How PAN is formed and how it gets its unique identity? \url{https://www.incometaxindia.gov.in/w/how-pan-is-formed-and-how-it-gets-its-unique-identity-}. Accessed 28 Oct 2026.",
 "rule114": r"Government of India. Income Tax Rules, 1962, Rule 114 (as amended): Application for and allotment of the Permanent Account Number. New Delhi, India: Central Board of Direct Taxes.",
 "raghuvanshi": r"Raghuvanshi SB, Girase S, Patil S, Chaudhari S, Ahirrao M. An end-to-end AI system for automated verification of Indian identity documents using OCR and large language models. Int J Adv Res Sci Commun Technol. 2025 Nov;160--9. " + doi("10.48175/ijarsct-29919") + ".",
 "panens": r"Devi VJLP, Gokula CSR, Gladence LM. A deep learning ensemble with OCR tools for PAN card recognition system. In: Proceedings of the 2025 12th International Conference on Computing for Sustainable Global Development (INDIACom); 2025 Apr 2--4; Delhi, India. Piscataway, NJ: IEEE; 2025. p. 1--6. " + doi("10.23919/INDIACom66777.2025.11115397") + ".",
 "dai": r"Dai K, Alonso J, Guti\'errez-Meana J. A machine learning framework for forgery detection in digital ID documents. J Innov Manag. 2025;13(2):XVI--XXV. " + doi("10.24840/2183-0606_013.002_l003") + ".",
 "limconnie": r"Lim EHY, Connie T. An explainable AI framework for identity document authentication in AML/KYC verification. Future Internet. 2026;18(9):485. " + doi("10.3390/fi18090485") + ".",
 "bae": r"Bae YY, Cho DJ, Jung KH. Enhancing document forgery detection with edge-focused deep learning. Symmetry (Basel). 2025;17(8):1208. " + doi("10.3390/sym17081208") + ".",
 "resnet": r"He K, Zhang X, Ren S, Sun J. Deep residual learning for image recognition. In: Proceedings of the 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR); 2016 Jun 27--30; Las Vegas, NV. Piscataway, NJ: IEEE; 2016. p. 770--8. " + doi("10.1109/CVPR.2016.90") + ".",
 "doctamper": r"Qu C, Liu C, Liu Y, Chen X, Peng D, Guo F, et al. Towards robust tampered text detection in document image: new dataset and new solution. In: Proceedings of the 2023 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR); 2023 Jun 17--24; Vancouver, BC, Canada. Piscataway, NJ: IEEE; 2023. p. 5937--46. " + doi("10.1109/CVPR52729.2023.00575") + ".",
 "midv": r"Bulatov KB, Emelianova EV, Tropin DV, Skoryukina NS, Chernyshova YS, Sheshkus AV, et al. MIDV-2020: a comprehensive benchmark dataset for identity document analysis. Comput Opt. 2022;46(2):252--70. " + doi("10.18287/2412-6179-CO-1006") + ".",
 "cmid": r"Mahfoudi G, Morain-Nicolier F, Retraint F, Pic M. CMID: a new dataset for copy-move forgeries on ID documents. In: Proceedings of the 2021 IEEE International Conference on Image Processing (ICIP); 2021 Sep 19--22; Anchorage, AK. Piscataway, NJ: IEEE; 2021. p. 3028--32. " + doi("10.1109/ICIP42928.2021.9506723") + ".",
 "trufor": r"Guillaro F, Cozzolino D, Sud A, Dufour N, Verdoliva L. TruFor: leveraging all-round clues for trustworthy image forgery detection and localization. In: Proceedings of the 2023 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR); 2023 Jun 17--24; Vancouver, BC, Canada. Piscataway, NJ: IEEE; 2023. p. 20606--15. " + doi("10.1109/CVPR52729.2023.01974") + ".",
 "morph": r"Makandar A, Javeriya SB. Enhancing Aadhar card image security with machine learning-based face morphing detection. In: Proceedings of the 2024 1st International Conference on Communications and Computer Science (InCCCS); 2024 May 22--24; Bangalore, India. Piscataway, NJ: IEEE; 2024. p. 1--6. " + doi("10.1109/InCCCS60947.2024.10593474") + ".",
 "guilloche": r"Al-Ghadi M, Ming Z, Gomez-Kr\"amer P, Burie JC. Identity documents authentication based on forgery detection of guilloche pattern. arXiv [Preprint]. 2022. " + doi("10.48550/arXiv.2206.10989") + ".",
 "pad": r"Ruiz EM, Tapia JE, Soto RT, Busch C. Identity card presentation attack detection: a systematic review. arXiv [Preprint]. 2025. " + doi("10.48550/arXiv.2511.06056") + ".",
 "flid": r"Kumar A, Tapwal R, Maple C, Hooper M. Field-localized forgery detection for digital identity documents. arXiv [Preprint]. 2026. " + doi("10.48550/arXiv.2605.09089") + ".",
 "shaikh": r"Shaikh M, Patil D. Image forgery/tampering detection using deep learning and cloud. Int J Innov Res Technol. 2022 Jun;9(1):1484--7.",
 "nirkhi": r"Nirkhi Singh S, Kakde S, Pimpalshende S, Govindwar S, Bhandari S, Raut T. Document forgery detection using OCR and deep learning. Int J Adv Res Sci Commun Technol. 2025 Nov;42--50. " + doi("10.48175/ijarsct-29906") + ".",
 "lalsudhesh": r"Lalsudhesh HA, Keerthana R, Radha N, Swathika R. PAN card tampering detection using machine learning techniques. In: Proceedings of the 2024 2nd International Conference on Inventive Computing and Informatics (ICICI); 2024 Jun 11--12; Bangalore, India. Piscataway, NJ: IEEE; 2024. p. 316--22. " + doi("10.1109/ICICI62254.2024.00059") + ".",
 "arora": r"Arora G, Ishwar AK, Verma S. PAN card tempering detection: a combined OCR and CNN methodology. In: Recent trends in intelligent computing and communication. Boca Raton, FL: CRC Press; 2025. p. 385--91. " + doi("10.1201/9781003593034-62") + ".",
 "hamza": r"Hamza MH, Kavitha KS, Patil S. Decentralized PAN card forgery and tampering detection using FLWR, CNN, OCR and Grad-CAM. In: Artificial intelligence based smart and secured applications. Cham, Switzerland: Springer; 2026. p. 262--76. (Communications in Computer and Information Science). " + doi("10.1007/978-3-032-17840-4_17") + ".",
 "muralikrishna": r"Murali Krishna N. AI-driven multimodal fraud detection framework for UID Aadhaar e-KYC using biometric and document verification. Commun Appl Nonlinear Anal. 2026;33(1s):299--308. " + doi("10.52783/cana.v33.6859") + ".",
 "idnet": r"Guan H, Wang Y, Xie L, Nag S, Goel R, Swamy NEN, et al. IDNet: a novel dataset for identity document analysis and fraud detection. arXiv [Preprint]. 2024. " + doi("10.48550/arXiv.2408.01690") + ".",
 "sidtd": r"Boned C, Talarmain M, Ghanmi N, Chiron G, Biswas S, Awal AM, et al. Synthetic dataset of ID and travel documents. Sci Data. 2024;11(1):1356. " + doi("10.1038/s41597-024-04160-9") + ".",
 "survey": r"Das G, Kumar C P, Ramachandra R. From forgeries to foundation models: a systematic survey of identity document attack and detection. arXiv [Preprint]. 2026. " + doi("10.48550/arXiv.2607.01442") + ".",
 "zhang": r"Zhang CJ, Gill AQ, Liu B, Anwar MJ. AI-based identity fraud detection: a systematic review. arXiv [Preprint]. 2025. " + doi("10.48550/arXiv.2501.09239") + ".",
 "augraphy": r"Groleau A, Chee KW, Larson S, Maini S, Boarman J. Augraphy: a data augmentation library for document images. In: Document analysis and recognition -- ICDAR 2023. Proceedings of the 17th International Conference on Document Analysis and Recognition; 2023 Aug 21--26; San Jos\'e, CA. Cham, Switzerland: Springer; 2023. p. 384--401. (Lecture Notes in Computer Science). " + doi("10.1007/978-3-031-41682-8_24") + ".",
 "wilson": r"Wilson EB. Probable inference, the law of succession, and statistical inference. J Am Stat Assoc. 1927;22(158):209--12. " + doi("10.1080/01621459.1927.10502953") + ".",
 "tesseract": r"Smith R. An overview of the Tesseract OCR engine. In: Proceedings of the Ninth International Conference on Document Analysis and Recognition (ICDAR 2007); 2007 Sep 23--26; Curitiba, Brazil. Piscataway, NJ: IEEE; 2007. p. 629--33. " + doi("10.1109/ICDAR.2007.4376991") + ".",
 "imagenet": r"Deng J, Dong W, Socher R, Li LJ, Li K, Fei-Fei L. ImageNet: a large-scale hierarchical image database. In: Proceedings of the 2009 IEEE Conference on Computer Vision and Pattern Recognition (CVPR); 2009 Jun 20--25; Miami, FL. Piscataway, NJ: IEEE; 2009. p. 248--55. " + doi("10.1109/CVPR.2009.5206848") + ".",
 "adamw": r"Loshchilov I, Hutter F. Decoupled weight decay regularization. In: Proceedings of the 7th International Conference on Learning Representations (ICLR 2019); 2019 May 6--9; New Orleans, LA. " + doi("10.48550/arXiv.1711.05101") + ".",
 "guo": r"Guo C, Pleiss G, Sun Y, Weinberger KQ. On calibration of modern neural networks. In: Precup D, Teh YW, editors. Proceedings of the 34th International Conference on Machine Learning (ICML 2017); 2017 Aug 6--11; Sydney, Australia. PMLR; 2017. p. 1321--30. (Proceedings of Machine Learning Research; vol. 70). \url{https://proceedings.mlr.press/v70/guo17a.html}.",
 "efron": r"Efron B, Tibshirani RJ. An introduction to the bootstrap. New York, NY: Chapman \& Hall; 1993. " + doi("10.1007/978-1-4899-4541-9") + ".",
 "holm": r"Holm S. A simple sequentially rejective multiple test procedure. Scand J Stat. 1979;6(2):65--70. \url{https://www.jstor.org/stable/4615733}.",
}

d = Path(sys.argv[1])
aux = (d / "manuscript.aux").read_text(encoding="utf-8")
order = []
for c in re.findall(r"\\citation\{([^}]*)\}", aux):
    for k in c.split(","):
        k = k.strip()
        if k and k not in order:
            order.append(k)
missing = [k for k in order if k not in R]
unused = [k for k in R if k not in order]
if missing:
    sys.exit(f"no formatted reference for: {missing}")
print(f"{len(order)} references in citation order; not cited: {unused}")
items = "\n".join("\\bibitem{%s}\n%s\n" % (k, R[k]) for k in order)
bib = "\\begin{thebibliography}{%d}\n%s\\end{thebibliography}" % (len(order), items)
tex = (d / "manuscript.tex").read_text(encoding="utf-8")
if "%%REFERENCES%%" in tex:
    tex = tex.replace("%%REFERENCES%%", bib)
else:
    tex = re.sub(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", lambda m: bib, tex, flags=re.S)
(d / "manuscript.tex").write_text(tex, encoding="utf-8")
